from code_engine import diagnose_static


def test_java_reversed_pass_fail_logic_detected_without_syntax_error():
    code = '''public class Main { public static void main(String[] args) { int marks = 75; if (marks >= 35) { System.out.println("Fail"); } else { System.out.println("Pass"); } } }'''
    result = diagnose_static(code, "Java")
    assert result["syntax_ok"] is True
    assert any("messages appear reversed" in issue for issue in result["issues"])
    assert not any("invalid syntax" in issue.lower() for issue in result["issues"])


def test_python_empty_collection_and_suspicious_average_adjustment():
    code = '''def calculate_average(numbers):\n    total = sum(numbers)\n    return total / len(numbers)\nnumbers = [10, 20, 30, 40]\naverage = calculate_average(numbers)\nprint("Average:", average + 10)'''
    result = diagnose_static(code, "Python")
    assert result["syntax_ok"] is True
    assert any("empty" in issue.lower() for issue in result["issues"])
    assert any("average/mean" in issue.lower() for issue in result["issues"])


def test_python_syntax_error_reports_line():
    result = diagnose_static("if True print('x')", "Python")
    assert result["syntax_ok"] is False
    assert any("Syntax error" in issue for issue in result["issues"])


def test_javascript_syntax_check_if_node_installed():
    result = diagnose_static("function broken( {", "JavaScript")
    if result["syntax_verified"]:
        assert result["syntax_ok"] is False
        assert any("JavaScript syntax error" in issue for issue in result["issues"])


def test_python_missing_colon_indent_and_typo_are_reported_without_execution():
    code = "for i in range(9)\npront(i("
    result = diagnose_static(code, "Python")
    assert result["syntax_ok"] is False
    assert any("line 1" in issue.lower() and "syntax error" in issue.lower() for issue in result["issues"])
    assert any("pront" in issue.lower() for issue in result["issues"])
    assert any("parenthesis" in issue.lower() for issue in result["issues"])
    assert len(result["issues"]) == len(set(result["issues"]))


def test_python_indentation_error_has_line_number():
    result = diagnose_static('def greet():\nprint("Hello")', "Python")
    assert result["syntax_ok"] is False
    assert any("line 2" in issue.lower() and "indented block" in issue.lower() for issue in result["issues"])


def test_auto_fix_accepts_expected_behavior_without_name_error(monkeypatch):
    import llm_service

    monkeypatch.setattr(llm_service, "_generate", lambda *args, **kwargs: "print('ok')")
    result = llm_service.auto_fix(
        "printt('ok')",
        "Python",
        "undefined name printt",
        1,
        model="test-model",
        expected_behavior="Should print ok",
    )
    assert result == "print('ok')"


def test_structured_refactor_accepts_expected_behavior_without_name_error(monkeypatch):
    import json
    import llm_service

    monkeypatch.setattr(
        llm_service,
        "_generate",
        lambda *args, **kwargs: json.dumps({"code": "print('ok')", "summary": "done", "changes": [], "risks": []}),
    )
    result = llm_service.structured_refactor(
        "printt('ok')",
        "Python",
        "fix issues",
        model="test-model",
        expected_behavior="Should print ok",
    )
    assert result["code"] == "print('ok')"
