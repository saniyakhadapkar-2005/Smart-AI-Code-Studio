"""FastAPI backend for Smart AI Code Studio.

The API is intentionally thin: business logic remains in the reusable
refactoring/code-engine modules, while FastAPI owns HTTP validation and routing.
"""
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import (
    AnalyzeResponse, CodeRequest, RefactorRequest, RefactorResponse,
    ValidationResponse, SUPPORTED_LANGUAGES,
)
from code_engine import analyze_code, compare_code, run_code, safety_scan, diagnose_static
from llm_service import auto_fix, ollama_health, structured_refactor, validate_with_llm
from refactor_engine import iterative_refactor

app = FastAPI(
    title="Smart AI Code Studio API",
    description="Local LLM-powered automated code refactoring backend.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_language(language: str) -> None:
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Choose one of: {', '.join(SUPPORTED_LANGUAGES)}"
        )

@app.get("/api/health")
def health(model: str = "qwen2.5-coder:7b"):
    """Return backend and local Ollama status."""
    ollama = ollama_health(model)
    return {
        "backend": "ok",
        "service": "Smart AI Code Studio API",
        "ollama": ollama,
    }

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: CodeRequest):
    validate_language(request.language)
    return {"metrics": analyze_code(request.code, request.language)}

@app.post("/api/validate", response_model=ValidationResponse)
def validate(request: CodeRequest):
    """AI-assisted defect review followed by real syntax/compiler/runtime checks.

    Reports issues found across attempts, even when a later attempt fixes them.
    Logic review is best-effort and cannot prove correctness without expected behavior/tests.
    """
    validate_language(request.language)
    original = request.code
    current = original
    issue_history = []
    last_output = ""
    last_summary = ""
    max_attempts = 3

    health_info = ollama_health(request.model)
    if not health_info["available"] or not health_info["model_installed"]:
        return {"success": False, "output": health_info["message"], "safety": safety_scan(current, request.language), "code": current, "issues": [health_info["message"]], "issue_history": [], "summary": "AI validation requires the local Ollama model.", "attempts": 0}

    for attempt in range(1, max_attempts + 1):
        safety = safety_scan(current, request.language)
        if safety["findings"] and not request.allow_risky:
            issue_history.extend({"attempt": attempt, "issue": item} for item in safety["findings"])
            return {"success": False, "output": "Execution blocked by safety check: " + ", ".join(safety["findings"]), "safety": safety, "code": current, "issues": safety["findings"], "issue_history": issue_history, "summary": "Unsafe operation detected; code was not executed.", "attempts": attempt}

        # AI reviews likely logic defects as well as syntax/structure before execution.
        review = validate_with_llm(current, request.language, model=request.model)
        last_summary = review.get("summary", "AI review completed.")
        issues = [str(x) for x in (review.get("issues", []) or [])]
        corrected = (review.get("corrected_code", "") or "").strip()
        for item in issues:
            record = {"attempt": attempt, "issue": item}
            if record not in issue_history:
                issue_history.append(record)

        if corrected and corrected != current and (not review.get("valid", False) or issues):
            current = corrected
            continue

        success, output = run_code(current, request.language, allow_risky=request.allow_risky)
        last_output = output
        if not success:
            runtime_issue = str(output)
            record = {"attempt": attempt, "issue": runtime_issue}
            if record not in issue_history:
                issue_history.append(record)
            issues = list(dict.fromkeys(issues + [runtime_issue]))

        if success and not issues:
            return {"success": True, "output": output, "safety": safety_scan(current, request.language), "code": current, "issues": [], "issue_history": issue_history, "summary": last_summary or "AI review and runtime checks passed.", "attempts": attempt}

        if attempt < max_attempts:
            fix_feedback = "\n".join(issues) if issues else "Review the code for obvious logic defects and edge cases."
            fixed = auto_fix(current, request.language, fix_feedback, attempt, model=request.model, expected_behavior=request.expected_behavior or "")
            if fixed and fixed != current:
                current = fixed
                continue

        return {"success": False, "output": last_output or "AI review found concerns that could not be confirmed as fixed.", "safety": safety_scan(current, request.language), "code": current, "issues": issues, "issue_history": issue_history, "summary": last_summary or "Validation found issues.", "attempts": attempt}

    return {"success": False, "output": last_output, "safety": safety_scan(current, request.language), "code": current, "issues": [x["issue"] for x in issue_history], "issue_history": issue_history, "summary": "Validation could not be completed.", "attempts": max_attempts}

@app.post("/api/refactor", response_model=RefactorResponse)
def refactor(request: RefactorRequest):
    validate_language(request.language)

    health_info = ollama_health(request.model)
    if not health_info["available"]:
        raise HTTPException(status_code=503, detail=health_info["message"])
    if not health_info["model_installed"]:
        raise HTTPException(status_code=503, detail=health_info["message"])

    before_metrics = analyze_code(request.code, request.language)

    try:
        result = iterative_refactor(
            request.code,
            request.language,
            request.goal,
            lambda c, l, g: structured_refactor(c, l, g, model=request.model, expected_behavior=request.expected_behavior or ""),
            lambda c, l, e, a: auto_fix(c, l, e, a, model=request.model, expected_behavior=request.expected_behavior or ""),
            max_attempts=request.max_attempts,
            allow_risky=request.allow_risky,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Refactoring pipeline failed: {exc}") from exc

    after_code = result.get("code", "")
    after_metrics = analyze_code(after_code, request.language)
    comparison = compare_code(request.code, after_code)

    return {
        "success": result["success"],
        "code": after_code,
        "language": request.language,
        "attempts": len(result.get("history", [])),
        "metadata": result.get("metadata", {}),
        "history": result.get("history", []),
        "before_metrics": before_metrics,
        "after_metrics": after_metrics,
        "comparison": comparison,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)


def _normalize_issue(issue: str) -> str:
    """Normalize issue text to prevent repeated/near-identical findings."""
    value = re.sub(r"^\s*(?:issue\s*\d+[:.)-]?\s*)?", "", str(issue), flags=re.I)
    value = re.sub(r"\b(line|at line)\s+\d+\b", r"\1 <line>", value, flags=re.I)
    value = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    # Collapse paraphrases into a small set of stable diagnostic categories.
    if "colon" in value and re.search(r"missing|expected|require|after the .* statement", value):
        return "missing colon"
    if "parenthesis" in value or "parentheses" in value or "unclosed parenthesis" in value:
        return "unclosed parenthesis"
    if "indentation" in value or "indented block" in value:
        return "indentation error"
    aliases = {
        "expected colon": "missing colon",
        "expected :": "missing colon",
        "missing :": "missing colon",
        "expected an indented block": "indentation error",
        "indentation error expected an indented block": "indentation error",
        "missing closing parenthesis": "unclosed parenthesis",
        "expected closing parenthesis": "unclosed parenthesis",
        "unmatched parenthesis": "unclosed parenthesis",
    }
    for source, target in aliases.items():
        if source in value:
            return target
    return value


@app.post("/api/diagnose")
def diagnose(request: CodeRequest):
    """Report source issues only. This endpoint never executes or edits submitted code."""
    validate_language(request.language)
    code = request.code or ""
    if not code.strip():
        raise HTTPException(status_code=400, detail="Enter source code first.")

    deterministic = diagnose_static(code, request.language)
    issues = list(deterministic.get("issues", []))
    health_info = ollama_health(request.model)
    ai_review_available = bool(health_info.get("available") and health_info.get("model_installed"))
    summary = "Language-specific static checks completed."

    # AI is a second opinion, never the syntax authority when a parser/compiler is available.
    if ai_review_available:
        try:
            review = validate_with_llm(code, request.language, model=request.model, expected_behavior=request.expected_behavior or "")
            for raw_issue in review.get("issues", []) or []:
                item = str(raw_issue).strip()
                if not item:
                    continue
                if deterministic.get("syntax_verified") and deterministic.get("syntax_ok") and re.search(r"syntax|invalid syntax|missing (?:colon|semicolon|brace|parenthesis)|compilation error|indentation", item, re.I):
                    continue
                # Do not invent a grading threshold when the user did not specify one.
                if (not request.expected_behavior and re.search(r"marks?\s*>=?\s*50|typical grading|passing threshold.*50", item, re.I)
                        and re.search(r"marks?\s*>=?\s*35", code, re.I)):
                    continue
                # De-duplicate AI wording against both deterministic and earlier AI findings.
                norm = _normalize_issue(item)
                if norm and all(_normalize_issue(existing) != norm for existing in issues):
                    issues.append(item)
            summary = str(review.get("summary", "Static checks and AI review completed."))
        except Exception as exc:
            summary = f"Static checks completed; AI review unavailable ({type(exc).__name__})."
    else:
        summary = "Static checks completed; local Ollama/model unavailable, so AI logic review was skipped."

    # Final exact/normalized de-duplication preserves the first, usually more precise finding.
    unique_issues = []
    seen = set()
    for issue in issues:
        norm = _normalize_issue(issue)
        if norm and norm not in seen:
            seen.add(norm)
            unique_issues.append(issue)

    return {
        "success": not unique_issues,
        "issues": unique_issues,
        "summary": summary,
        "ai_review": ai_review_available,
        "syntax_verified": deterministic.get("syntax_verified", False),
        "syntax_ok": deterministic.get("syntax_ok", False),
        "source_changed": False,
        "executed": False,
        "limitations": "Static analysis catches known patterns; AI logic review is best-effort. Provide expected behavior/tests for stronger verification.",
    }
