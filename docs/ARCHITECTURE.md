# Architecture

## Layers

### 1. Frontend
`app.py` is the Streamlit presentation layer. It collects code and settings, calls REST APIs, and renders results.

### 2. API backend
`backend/main.py` is the FastAPI HTTP layer. It validates requests and routes them to reusable application modules.

Endpoints:
- `GET /api/health`
- `POST /api/analyze`
- `POST /api/validate`
- `POST /api/refactor`

### 3. Application engines
- `code_engine.py`: static analysis, safety scan, execution/compilation and code comparison.
- `refactor_engine.py`: iterative refactor → validate → error-feedback → auto-fix loop.
- `llm_service.py`: Ollama communication, prompt construction and structured LLM output parsing.

### 4. LLM runtime
Ollama hosts the local Llama 3 model. No paid cloud LLM API is required.

## End-to-end request

```text
Streamlit
  -> POST /api/refactor
FastAPI
  -> analyze original code
  -> call refactoring engine
Refactoring engine
  -> prompt Ollama/Llama 3
  -> safety scan
  -> compile/execute
  -> if failure: send error back to LLM
  -> repeat up to 3 attempts
FastAPI
  -> diff + quality + history
Streamlit
  -> render final result
```

## Why the separation matters

The frontend does not own LLM or execution logic. This makes the application easier to test, maintain and replace with another frontend later. The FastAPI layer also gives the project a clear REST contract that can be tested independently of the UI.
