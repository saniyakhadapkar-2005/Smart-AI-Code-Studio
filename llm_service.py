"""Local Ollama LLM integration for Smart AI Code Studio."""

from __future__ import annotations

import json
import re
from typing import Dict

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5-coder:7b"


def _extract_json(text: str) -> Dict:
    """Extract JSON from normal JSON, markdown JSON, or common pseudo-JSON model output."""
    text = (text or "").strip()
    if not text:
        return {}

    candidates = [text]
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.I | re.S)
    if fenced:
        candidates.insert(0, fenced.group(1).strip())

    for candidate in candidates:
        try:
            value = json.loads(candidate)
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            pass

    # Some local models return Python-style pseudo JSON with triple-quoted code.
    code_match = re.search(r'(["\']?code["\']?)\s*:\s*"""(.*?)"""', text, flags=re.I | re.S)
    if code_match:
        code = code_match.group(2).strip()
        summary_match = re.search(r'(["\']?summary["\']?)\s*:\s*["\'](.*?)["\']\s*,\s*(["\']?changes["\']?)', text, flags=re.I | re.S)
        summary = summary_match.group(2).strip() if summary_match else "AI refactoring completed."
        changes_match = re.search(r'(["\']?changes["\']?)\s*:\s*\[(.*?)\]', text, flags=re.I | re.S)
        changes = re.findall(r'["\']([^"\']+)["\']', changes_match.group(2)) if changes_match else []
        risks_match = re.search(r'(["\']?risks["\']?)\s*:\s*\[(.*?)\]', text, flags=re.I | re.S)
        risks = re.findall(r'["\']([^"\']+)["\']', risks_match.group(2)) if risks_match else []
        return {"code": code, "summary": summary, "changes": changes, "risks": risks}

    # Last attempt: locate a JSON object and decode it.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            value = json.loads(text[start:end + 1])
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            pass
    return {}


def ollama_health(model: str = DEFAULT_MODEL) -> Dict:
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code != 200:
            return {"available": False, "message": f"Ollama returned HTTP {response.status_code}."}
        models = [m.get("name", "") for m in response.json().get("models", [])]
        installed = model in models or any(name.startswith(model + ":") for name in models)
        return {
            "available": True,
            "model_installed": installed,
            "models": models,
            "message": "Ollama is running." + (f" {model} is available." if installed else f" {model} was not found."),
        }
    except requests.RequestException:
        return {"available": False, "model_installed": False, "models": [], "message": "Ollama is not reachable at localhost:11434."}


def _generate(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 180) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2},
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json().get("response", "")


def structured_refactor(
    code: str,
    language: str,
    goal: str,
    model: str = DEFAULT_MODEL,
    expected_behavior: str = "",
) -> Dict:
    prompt = f"""You are a senior {language} developer and code-refactoring assistant.
Refactor the provided code while preserving its intended behavior.
Goal: {goal}
Rules:
- Return valid executable {language} code inside the JSON field `code`.
- Do not invent missing requirements.
- First inspect the code for syntax errors and obvious defects: missing brackets, parentheses or braces, missing colons/semicolons, invalid syntax, indentation errors, undefined names, malformed blocks, and obvious logic mistakes.
- Fix those defects before refactoring.
- Preserve the intended behavior and do not change correct behavior just for style.
- Improve readability, maintainability, efficiency and error handling where appropriate.
- Do not add external dependencies unless absolutely necessary.
- The `changes` list must describe ONLY changes actually present in the returned code.
- Return ONLY a valid JSON object using this exact structure:
{{
  "code": "complete refactored source code as a JSON string",
  "summary": "short summary",
  "changes": ["actual change 1", "actual change 2"],
  "risks": []
}}

SOURCE EXPECTED BEHAVIOR / OUTPUT (user-provided; may be empty):
{expected_behavior or "Not provided"}

CODE:
{code}
"""
    raw = _generate(prompt, model=model)
    data = _extract_json(raw)
    if data.get("code"):
        return {
            "code": str(data["code"]).strip(),
            "summary": str(data.get("summary", "AI refactoring completed.")),
            "changes": data.get("changes", []) if isinstance(data.get("changes", []), list) else [],
            "risks": data.get("risks", []) if isinstance(data.get("risks", []), list) else [],
        }

    # Fallback for models that ignore the JSON instruction.
    cleaned = re.sub(r"^```(?:python|java|cpp|javascript|js|c\+\+)?\s*|\s*```$", "", raw.strip(), flags=re.I).strip()
    return {"code": cleaned, "summary": "AI refactoring completed.", "changes": [], "risks": []}


def auto_fix(
    code: str,
    language: str,
    error: str,
    attempt: int,
    model: str = DEFAULT_MODEL,
    expected_behavior: str = "",
) -> str:
    prompt = f"""You are debugging a {language} program.
Attempt: {attempt}
Fix the validation error below while preserving the intended behavior.
Also inspect the current code for related syntax/structure problems such as missing brackets, parentheses or braces, indentation errors, malformed blocks, undefined names, and obvious logic mistakes that could cause the reported failure.
Return ONLY the complete executable code. No Markdown, JSON, or explanation.

ERROR:
{error}

CURRENT EXPECTED BEHAVIOR / OUTPUT (user-provided; may be empty):
{expected_behavior or "Not provided"}

CODE:
{code}
"""
    raw = _generate(prompt, model=model)
    cleaned = re.sub(r"^```(?:python|java|cpp|javascript|js|c\+\+)?\s*|\s*```$", "", raw.strip(), flags=re.I).strip()
    # If a model still returns a JSON object, extract its code field.
    parsed = _extract_json(cleaned)
    if parsed.get("code"):
        cleaned = str(parsed["code"]).strip()
    return cleaned


def validate_with_llm(code: str, language: str, model: str = DEFAULT_MODEL, expected_behavior: str = "") -> Dict:
    """Ask the local LLM to review code for syntax/structure and obvious logic defects.

    This complements compiler/runtime checks. It cannot prove arbitrary business logic
    correctness without tests or a formal specification.
    """
    prompt = f"""You are a senior {language} code reviewer.
Review the code for defects BEFORE saying it is valid. Infer the apparent intent from function names, variable names, comments, examples and surrounding code. Distinguish definite defects from uncertain concerns. Do not mark a logic bug merely because you prefer another style.
Check all of these categories:
- missing colon, semicolon, bracket, parenthesis or brace
- indentation and malformed blocks
- invalid syntax or compilation problems
- undefined names/variables and obvious type/API misuse
- unreachable or contradictory branches
- off-by-one errors, wrong conditions, incorrect loop behavior
- incorrect calculations, wrong operators, accidental infinite loops
- obvious edge-case failures such as empty input or division by zero
- other obvious logic errors relative to the code's apparent intent
- compare sample inputs with the apparent expected behavior when inferable; identify suspicious hard-coded values, swapped variables, incorrect return values, and calculations that contradict function names/comments

Do not invent requirements. If behavior is ambiguous, mark it as a concern rather than a definite bug. A deterministic parser/compiler is more authoritative for syntax than your opinion. Do not report a syntax error unless you can identify a concrete malformed token or line.
If you find a clear defect, return corrected complete executable code. For logic bugs, explain the exact mismatch between the apparent intended behavior and current behavior in `issues`. If the intent is ambiguous, report a concern and do not make a speculative behavior change.
Return ONLY this JSON object:
{{
  "valid": true,
  "issues": ["short issue 1"],
  "corrected_code": "complete code or empty string if no correction is needed",
  "summary": "short review summary"
}}

EXPECTED BEHAVIOR / OUTPUT (user-provided; may be empty):
{expected_behavior or "Not provided"}

CODE:
{code}
"""
    raw = _generate(prompt, model=model, timeout=180)
    data = _extract_json(raw)
    if not data:
        return {"valid": False, "issues": ["AI validation returned an unreadable response."], "corrected_code": "", "summary": "AI review could not be parsed."}
    issues = data.get("issues", [])
    if not isinstance(issues, list):
        issues = [str(issues)] if issues else []
    corrected = data.get("corrected_code", "")
    if corrected is None:
        corrected = ""
    return {
        "valid": bool(data.get("valid", not issues)),
        "issues": [str(x) for x in issues],
        "corrected_code": str(corrected).strip(),
        "summary": str(data.get("summary", "AI review completed.")),
    }
