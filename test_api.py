"""API tests for analyze/validate paths. Ollama is mocked for deterministic tests."""
from fastapi.testclient import TestClient
import backend.main as backend_main
from backend.main import app

client = TestClient(app)


def test_analyze():
    response = client.post("/api/analyze", json={
        "code": "def add(a, b):\n    return a + b\n",
        "language": "Python",
    })
    assert response.status_code == 200
    assert "quality_score" in response.json()["metrics"]


def test_unsupported_language():
    response = client.post("/api/analyze", json={
        "code": "print('hello')",
        "language": "Ruby",
    })
    assert response.status_code == 400


def test_validate_safe_python(monkeypatch):
    monkeypatch.setattr(backend_main, "ollama_health", lambda model: {
        "available": True, "model_installed": True, "message": "ok"
    })
    monkeypatch.setattr(backend_main, "validate_with_llm", lambda code, language, model: {
        "valid": True, "issues": [], "corrected_code": "", "summary": "Looks good."
    })
    response = client.post("/api/validate", json={
        "code": "print('hello')",
        "language": "Python",
    })
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_validate_can_return_ai_fix(monkeypatch):
    monkeypatch.setattr(backend_main, "ollama_health", lambda model: {
        "available": True, "model_installed": True, "message": "ok"
    })
    calls = {"n": 0}
    def fake_validate(code, language, model):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "valid": False,
                "issues": ["Missing colon after for statement."],
                "corrected_code": "for i in range(3):\n    print(i)\n",
                "summary": "Fixed syntax issue."
            }
        return {"valid": True, "issues": [], "corrected_code": "", "summary": "Looks good."}
    monkeypatch.setattr(backend_main, "validate_with_llm", fake_validate)
    response = client.post("/api/validate", json={
        "code": "for i in range(3)\n    print(i)\n",
        "language": "Python",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert ":" in data["code"]
