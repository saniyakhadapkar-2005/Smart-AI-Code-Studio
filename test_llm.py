"""Small Ollama connectivity test. Run after starting Ollama and pulling the selected model."""

from llm_service import DEFAULT_MODEL, ollama_health

if __name__ == "__main__":
    result = ollama_health(DEFAULT_MODEL)
    print(result)
