"""Core code analysis, validation, safety and comparison utilities."""

from __future__ import annotations

import ast
import difflib
import io
import re
import shutil
import subprocess
import tempfile
from typing import Dict, List, Tuple


LANG_EXTENSIONS = {
    "Python": "py",
    "Java": "java",
    "C++": "cpp",
    "JavaScript": "js",
}


def clean_code(code: str) -> str:
    if not code:
        return ""
    code = code.strip()
    # Remove Markdown fences while preserving the actual code.
    code = re.sub(r"^```(?:python|java|cpp|javascript|js|c\+\+)?\s*", "", code, flags=re.I)
    code = re.sub(r"\s*```$", "", code)
    return code.strip()


def wrap_java_code(code: str) -> str:
    if re.search(r"\bclass\s+\w+", code):
        return code
    return (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        + "\n".join("        " + line for line in code.splitlines())
        + "\n    }\n}"
    )


def normalize_java_main_class(code: str) -> str:
    """Make a public Java class compatible with the temporary Main.java filename."""
    if re.search(r"\bpublic\s+class\s+\w+", code):
        code = re.sub(r"\bpublic\s+class\s+\w+", "public class Main", code, count=1)
    return code


def safety_scan(code: str, language: str) -> Dict:
    """Static pre-execution safety check. This is a warning/blocking layer, not a sandbox."""
    patterns = {
        "Python": [
            (r"\b(os\.system|subprocess\.|Popen\s*\()", "OS/process execution"),
            (r"\b(shutil\.rmtree|os\.remove|os\.unlink)\b", "file deletion"),
            (r"\b(eval|exec)\s*\(", "dynamic code execution"),
            (r"\b(socket\.|requests\.|urllib\.)", "network access"),
        ],
        "Java": [
            (r"\bRuntime\.getRuntime\(\)\.exec", "OS/process execution"),
            (r"\bProcessBuilder\s*\(", "process execution"),
            (r"\bFiles\.(delete|deleteIfExists)\b", "file deletion"),
            (r"\b(URL|HttpClient|Socket)\b", "network access"),
        ],
        "C++": [
            (r"\bsystem\s*\(", "OS/process execution"),
            (r"\bremove\s*\(", "file deletion"),
            (r"\b(socket|curl|wget)\b", "network access"),
        ],
        "JavaScript": [
            (r"\b(child_process|exec|spawn|execSync)\b", "process execution"),
            (r"\b(fs\.(unlink|rm|rmdir)|unlinkSync|rmSync)\b", "file deletion"),
            (r"\b(fetch|axios|http|https)\b", "network access"),
            (r"\beval\s*\(", "dynamic code execution"),
        ],
    }
    findings = []
    for pattern, category in patterns.get(language, []):
        if re.search(pattern, code, flags=re.I):
            findings.append(category)
    findings = sorted(set(findings))
    return {
        "safe": not findings,
        "risk_level": "HIGH" if findings else "LOW",
        "findings": findings,
        "message": "Potentially risky operations detected." if findings else "No high-risk execution patterns detected.",
    }


def _python_metrics(code: str) -> Dict:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {"syntax_error": f"Line {exc.lineno}: {exc.msg}"}

    functions = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
    classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
    loops = sum(isinstance(n, (ast.For, ast.AsyncFor, ast.While)) for n in ast.walk(tree))
    conditionals = sum(isinstance(n, ast.If) for n in ast.walk(tree))
    imports = sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))
    branches = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp, ast.IfExp)) for n in ast.walk(tree))
    comments = sum(1 for line in code.splitlines() if line.strip().startswith("#"))
    return {
        "syntax_error": None,
        "functions": functions,
        "classes": classes,
        "loops": loops,
        "conditionals": conditionals,
        "imports": imports,
        "branches": branches,
        "comments": comments,
    }


def analyze_code(code: str, language: str) -> Dict:
    code = code or ""
    lines = code.splitlines()
    nonblank = [line for line in lines if line.strip()]
    comments = sum(1 for line in lines if line.strip().startswith(("#", "//", "/*", "*")))
    long_lines = sum(1 for line in lines if len(line) > 100)
    duplicate_lines = len(nonblank) - len(set(nonblank))

    result = {
        "language": language,
        "functions": 0,
        "classes": 0,
        "variables": len(re.findall(r"\b[A-Za-z_]\w*\s*=", code)),
        "loops": len(re.findall(r"\b(for|while)\b", code)),
        "conditionals": len(re.findall(r"\b(if|elif|else if|switch|case)\b", code)),
        "imports": len(re.findall(r"\b(import|include|require)\b", code)),
        "comments": comments,
        "loc_total": len(lines),
        "loc_code": len(nonblank),
        "loc_blank": len(lines) - len(nonblank),
        "long_lines": long_lines,
        "duplicate_lines": max(0, duplicate_lines),
        "complexity": 1 + len(re.findall(r"\b(if|elif|else if|for|while|case|catch|except)\b", code)),
        "syntax_error": None,
    }

    if language == "Python":
        result.update(_python_metrics(code))
        if result.get("syntax_error"):
            result["syntax_error"] = result["syntax_error"]
    else:
        result["functions"] = len(re.findall(r"\b(?:void|int|float|double|String|function|def)\s+\w+\s*\(", code))
        result["classes"] = len(re.findall(r"\bclass\s+\w+", code))

    risk = safety_scan(code, language)
    result["risk_level"] = risk["risk_level"]
    result["risk_findings"] = risk["findings"]

    score = 100
    score -= min(25, result["complexity"] * 2)
    score -= min(20, result["long_lines"] * 2)
    score -= min(15, result["duplicate_lines"] * 2)
    if result["syntax_error"]:
        score -= 30
    if risk["findings"]:
        score -= min(20, len(risk["findings"]) * 5)
    if result["loc_code"] and result["comments"] == 0:
        score -= 5
    result["quality_score"] = max(0, min(100, score))
    return result


def compare_code(before: str, after: str) -> Dict:
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    added = sum(1 for line in difflib.ndiff(before_lines, after_lines) if line.startswith("+ "))
    removed = sum(1 for line in difflib.ndiff(before_lines, after_lines) if line.startswith("- "))
    diff = "\n".join(difflib.unified_diff(before_lines, after_lines, fromfile="Original", tofile="Refactored", lineterm=""))
    return {"added": added, "removed": removed, "diff": diff}


def _run_process(args: List[str], timeout: int = 10, cwd: str | None = None) -> Tuple[bool, str]:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired:
        return False, f"Execution timed out after {timeout} seconds."
    except Exception as exc:
        return False, str(exc)
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output.strip() or "No Output"


def run_code(code: str, language: str, allow_risky: bool = False) -> Tuple[bool, str]:
    code = clean_code(code)
    if not code:
        return False, "No code provided."

    risk = safety_scan(code, language)
    if risk["findings"] and not allow_risky:
        return False, "Execution blocked by safety check: " + ", ".join(risk["findings"]) + ". Enable the risk override only for code you trust."

    try:
        if language == "Python":
            # Compile first; then execute in a child process with a timeout.
            compile(code, "<user_code>", "exec")
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
                f.write(code)
                path = f.name
            try:
                return _run_process([shutil.which("python") or "python", path])
            finally:
                try:
                    import os
                    os.unlink(path)
                except OSError:
                    pass

        if language == "Java":
            if shutil.which("javac") is None or shutil.which("java") is None:
                return False, "Java compiler/runtime (javac/java) was not found on this system."
            code = normalize_java_main_class(wrap_java_code(code))
            with tempfile.TemporaryDirectory() as temp_dir:
                path = f"{temp_dir}/Main.java"
                with open(path, "w", encoding="utf-8") as f:
                    f.write(code)
                ok, output = _run_process(["javac", path])
                if not ok:
                    return False, output
                return _run_process(["java", "-cp", temp_dir, "Main"])

        if language == "C++":
            if shutil.which("g++") is None:
                return False, "C++ compiler (g++) was not found on this system."
            with tempfile.TemporaryDirectory() as temp_dir:
                src = f"{temp_dir}/main.cpp"
                exe = f"{temp_dir}/main.exe"
                with open(src, "w", encoding="utf-8") as f:
                    f.write(code)
                ok, output = _run_process(["g++", src, "-o", exe], timeout=20)
                if not ok:
                    return False, output
                return _run_process([exe])

        if language == "JavaScript":
            if shutil.which("node") is None:
                return False, "JavaScript runtime (node) was not found on this system."
            with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w", encoding="utf-8") as f:
                f.write(code)
                path = f.name
            try:
                return _run_process(["node", path])
            finally:
                try:
                    import os
                    os.unlink(path)
                except OSError:
                    pass

        return False, f"Unsupported language: {language}"
    except SyntaxError as exc:
        return False, f"Syntax error at line {exc.lineno}: {exc.msg}"
    except Exception as exc:
        return False, str(exc)


def _line_of_match(code: str, pattern: str, flags: int = re.I):
    match = re.search(pattern, code, flags)
    return code.count("\n", 0, match.start()) + 1 if match else None


def diagnose_static(code: str, language: str) -> Dict:
    """Non-executing, multi-language diagnostics with conservative fallbacks.

    Compiler/parser output is authoritative for syntax when the tool exists. Heuristics
    cover common defects, but cannot prove arbitrary program logic correct.
    """
    code = clean_code(code or "")
    issues: List[str] = []
    syntax_verified = False
    syntax_ok = False
    if not code.strip():
        return {"issues": ["Line 1: Enter source code first."], "syntax_verified": False, "syntax_ok": False}

    def add(message: str):
        # Keep same-line same-category findings from being reported twice.
        normalized = re.sub(r"[^a-z0-9]+", " ", message.lower()).strip()
        if normalized and all(re.sub(r"[^a-z0-9]+", " ", old.lower()).strip() != normalized for old in issues):
            issues.append(message)

    # Syntax/compile checks. These tools only parse/compile; they do not run submitted code.
    if language == "Python":
        try:
            tree = ast.parse(code, filename="<submitted_code>")
            compile(tree, "<submitted_code>", "exec")
            syntax_verified = syntax_ok = True
        except (SyntaxError, IndentationError, TabError) as exc:
            syntax_verified = True
            syntax_ok = False
            line = getattr(exc, "lineno", None) or 1
            message = getattr(exc, "msg", None) or str(exc)
            add(f"Syntax error — line {line}: {message}.")
            # Add only high-confidence, distinct secondary hints; parser stops at first error.
            parser_line = line
            for number, text in enumerate(code.splitlines(), 1):
                if number != parser_line and re.match(r"^\s*(?:for|while|if|elif|else|try|except|finally|def|class|with)\b.*[^:]\s*$", text) and not text.rstrip().endswith(":") and not text.strip().startswith("#"):
                    add(f"Line {number}: missing colon ':' at the end of this Python statement.")
                if re.search(r"\bpront\s*\(", text):
                    add(f"Line {number}: 'pront' looks like a misspelling of 'print'.")
                if text.count("(") > text.count(")"):
                    add(f"Line {number}: possible missing closing parenthesis ')'.")
            return {"issues": issues, "syntax_verified": syntax_verified, "syntax_ok": False}

        # Conservative Python semantic/static checks.
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv)):
                if isinstance(node.right, ast.Call) and isinstance(node.right.func, ast.Name) and node.right.func.id == "len":
                    add(f"Line {node.lineno}: possible division by zero if the collection is empty; handle the empty-input case.")
            if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.left, ast.Constant) and isinstance(node.comparators[0], ast.Constant):
                add(f"Line {node.lineno}: comparison uses two constants; verify that this condition is intentional.")
        # Optional semantic/lint pass. It parses source only and never executes it.
        pyflakes_available = False
        try:
            from pyflakes.api import check as pyflakes_check
            from pyflakes.reporter import Reporter
            output = io.StringIO()
            reporter = Reporter(output, output)
            pyflakes_check(code, "<submitted_code>", reporter)
            pyflakes_available = True
            for diagnostic in output.getvalue().splitlines():
                match = re.match(r"<submitted_code>:(\d+):(\d+):\s*(.*)", diagnostic)
                if not match:
                    continue
                number, _column, detail = int(match.group(1)), int(match.group(2)), match.group(3)
                if re.search(r"undefined name ['\"](?:pront|printt|pritn|prnit)['\"]", detail, re.I):
                    typo = re.search(r"['\"](pront|printt|pritn|prnit)['\"]", detail, re.I).group(1)
                    add(f"Line {number}: '{typo}' is not defined; check the spelling (for example, 'print').")
                elif re.search(r"undefined name|referenced before assignment|assigned to before global declaration|imported but unused|local variable .* assigned to but never used", detail, re.I):
                    add(f"Line {number}: semantic/lint issue: {detail}")
        except ImportError:
            pass
        for number, text in enumerate(code.splitlines(), 1):
            if re.search(r"\b(?:pront|printt|pritn|prnit)\s*\(", text) and not pyflakes_available:
                typo = re.search(r"\b(pront|printt|pritn|prnit)\s*\(", text).group(1)
                add(f"Line {number}: '{typo}' looks like a misspelling of the 'print' function.")

    elif language == "Java":
        if shutil.which("javac"):
            java_source = normalize_java_main_class(wrap_java_code(code))
            with tempfile.TemporaryDirectory() as td:
                src = f"{td}/Main.java"
                with open(src, "w", encoding="utf-8") as f:
                    f.write(java_source)
                ok, output = _run_process(["javac", "-Xlint:none", src], timeout=15)
            syntax_verified = True
            syntax_ok = ok
            if not ok:
                for item in [x.strip() for x in output.splitlines() if x.strip()][:5]:
                    if re.search(r"\.java:\d+: error:", item):
                        add("Java compiler: " + item.replace(src, "source"))
                if not issues:
                    add("Java compiler error: " + " | ".join(x.strip() for x in output.splitlines() if x.strip())[:700])
                return {"issues": issues, "syntax_verified": True, "syntax_ok": False}
        else:
            syntax_verified = False
            syntax_ok = True
            if code.count("{") != code.count("}"):
                add("Possible syntax issue: opening and closing braces do not match; javac is unavailable for a full check.")
                syntax_ok = False
            if code.count("(") != code.count(")"):
                add("Possible syntax issue: opening and closing parentheses do not match; javac is unavailable for a full check.")
                syntax_ok = False

    elif language == "C++":
        if shutil.which("g++"):
            with tempfile.TemporaryDirectory() as td:
                src = f"{td}/main.cpp"
                with open(src, "w", encoding="utf-8") as f:
                    f.write(code)
                ok, output = _run_process(["g++", "-std=c++17", "-fsyntax-only", src], timeout=20)
            syntax_verified = True
            syntax_ok = ok
            if not ok:
                for item in [x.strip() for x in output.splitlines() if x.strip()][:5]:
                    if re.search(r"main\.cpp:\d+:\d+: (?:error|warning):", item):
                        add("C++ compiler: " + item)
                if not issues:
                    add("C++ compiler error: " + " | ".join(x.strip() for x in output.splitlines() if x.strip())[:700])
                return {"issues": issues, "syntax_verified": True, "syntax_ok": False}
        else:
            syntax_verified = False
            syntax_ok = True
            if code.count("{") != code.count("}"):
                add("Possible syntax issue: opening and closing braces do not match; g++ is unavailable for a full check.")
                syntax_ok = False
            if code.count("(") != code.count(")"):
                add("Possible syntax issue: opening and closing parentheses do not match; g++ is unavailable for a full check.")
                syntax_ok = False

    elif language == "JavaScript":
        if shutil.which("node"):
            with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w", encoding="utf-8") as f:
                f.write(code)
                src = f.name
            try:
                ok, output = _run_process(["node", "--check", src], timeout=15)
            finally:
                try:
                    import os
                    os.unlink(src)
                except OSError:
                    pass
            syntax_verified = True
            syntax_ok = ok
            if not ok:
                for item in [x.strip() for x in output.splitlines() if x.strip()][:4]:
                    if re.search(r"SyntaxError|\.js:\d+", item, re.I):
                        add("JavaScript syntax error: " + item[:300])
                if not issues:
                    add("JavaScript syntax error: " + " | ".join(x.strip() for x in output.splitlines() if x.strip())[:700])
                return {"issues": issues, "syntax_verified": True, "syntax_ok": False}
        else:
            syntax_verified = False
            syntax_ok = True
            if code.count("{") != code.count("}"):
                add("Possible syntax issue: opening and closing braces do not match; Node.js is unavailable for a full check.")
                syntax_ok = False
            if code.count("(") != code.count(")"):
                add("Possible syntax issue: opening and closing parentheses do not match; Node.js is unavailable for a full check.")
                syntax_ok = False

    # High-confidence cross-language logic heuristic. Do not assume a grading threshold.
    if re.search(r'\bif\s*\(?\s*marks?\s*>=\s*\d+\s*\)?\s*\{?\s*(?:System\.out\.println|console\.log|print)\s*\(\s*["\']Fail["\']', code, re.I | re.S):
        if re.search(r'\belse\s*\{?\s*(?:System\.out\.println|console\.log|print)\s*\(\s*["\']Pass["\']', code, re.I | re.S):
            line = _line_of_match(code, r'["\']Fail["\']') or 1
            add(f"Line {line}: likely logic issue — messages appear reversed: the passing condition prints 'Fail' and the else branch prints 'Pass'; verify the intended threshold.")
    if re.search(r"\b(?:average|avg|mean)\b", code, re.I) and re.search(r"(?:average|avg|mean)\s*\+\s*\d+", code, re.I):
        line = _line_of_match(code, r"(?:average|avg|mean)\s*\+\s*\d+") or 1
        add(f"Line {line}: possible calculation issue — average/mean is increased by a constant; confirm this is intentional.")

    return {"issues": issues, "syntax_verified": syntax_verified, "syntax_ok": syntax_ok}

