from fastapi.testclient import TestClient

import backend.main as backend_main


def test_diagnose_is_report_only_and_deduplicates(monkeypatch):
    monkeypatch.setattr(
        backend_main,
        "ollama_health",
        lambda model: {"available": True, "model_installed": True, "message": "ok"},
    )
    monkeypatch.setattr(
        backend_main,
        "validate_with_llm",
        lambda *args, **kwargs: {
            "valid": False,
            "issues": ["Missing colon after the for statement", "The for statement is missing a colon"],
            "corrected_code": "",
            "summary": "AI review done",
        },
    )
    client = TestClient(backend_main.app)
    original = "for i in range(9)\n    print(i)"
    response = client.post(
        "/api/diagnose",
        json={"code": original, "language": "Python", "model": "test-model"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["executed"] is False
    assert data["source_changed"] is False
    # Static parser and two AI phrasings should not create three copies of one colon issue.
    colon_issues = [x for x in data["issues"] if "colon" in x.lower()]
    assert len(colon_issues) == 1
