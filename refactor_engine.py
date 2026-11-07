"""Iterative LLM refactoring and validation engine."""

from __future__ import annotations

from typing import Callable, Dict

from code_engine import analyze_code, clean_code, normalize_java_main_class, run_code, safety_scan, wrap_java_code


def iterative_refactor(
    original_code: str,
    language: str,
    goal: str,
    llm_refactor: Callable,
    llm_fix: Callable,
    max_attempts: int = 3,
    allow_risky: bool = False,
) -> Dict:
    result = llm_refactor(original_code, language, goal)
    current = clean_code(result.get("code", ""))
    if language == "Java":
        current = normalize_java_main_class(wrap_java_code(current))

    history = []
    if not current:
        return {"success": False, "code": "", "history": [{"attempt": 1, "success": False, "error": "LLM returned empty code."}], "metadata": result}

    for attempt in range(1, max_attempts + 1):
        risk = safety_scan(current, language)
        if risk["findings"] and not allow_risky:
            history.append({"attempt": attempt, "success": False, "error": "Blocked by safety check: " + ", ".join(risk["findings"]), "risk": risk})
            return {"success": False, "code": current, "history": history, "metadata": result}

        success, output = run_code(current, language, allow_risky=allow_risky)
        history.append({"attempt": attempt, "success": success, "error": "" if success else output, "output": output if success else "", "risk": risk})
        if success:
            return {
                "success": True,
                "code": current,
                "history": history,
                "metadata": result,
                "analysis": analyze_code(current, language),
            }
        if attempt < max_attempts:
            current = clean_code(llm_fix(current, language, output, attempt))
            if language == "Java":
                current = normalize_java_main_class(wrap_java_code(current))

    return {"success": False, "code": current, "history": history, "metadata": result, "analysis": analyze_code(current, language)}
