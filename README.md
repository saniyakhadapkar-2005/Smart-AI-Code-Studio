# Smart AI Code Studio

A local-first Generative AI application for automated source-code refactoring, validation and iterative error correction.

## Architecture

```text
User
  ↓
Streamlit Frontend
  ↓ HTTP/REST
FastAPI Backend
  ↓
Refactoring / Analysis / Validation Engines
  ↓
Ollama → Llama 3
  ↓
Generated Code
  ↓
Safety Check
  ↓
Compile / Execute
  ├── PASS → Final Result
  └── FAIL → Error Feedback → LLM Auto-Fix → Validate Again
```

## Key capabilities

1. **Iterative LLM Auto-Fix** — validates generated code and feeds compiler/runtime errors back to the LLM for up to 3 attempts.
2. **Before/After Diff** — shows exactly what changed.
3. **Quality Report** — compares code metrics before and after refactoring.
4. **Static Analysis** — functions, classes, variables, loops, conditionals, imports, LOC, long lines and complexity indicators.
5. **Safety Layer** — blocks selected high-risk execution patterns by default.
6. **Refactoring History** — keeps the latest session results in the UI.
7. **Structured LLM Output** — the refactoring prompt requests code, summary, changes and risks.
8. **Backend Architecture** — Streamlit is the frontend and FastAPI exposes REST endpoints for analysis, validation and refactoring.

## Supported languages

- Python
- Java
- C++
- JavaScript

## Technology stack

- Python
- Streamlit
- FastAPI
- Pydantic
- Ollama
- Llama 3
- Requests
- Static analysis with Python AST/regex
- Git/GitHub

## Run locally

### 1. Install dependencies

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Install and start Ollama

Make sure Ollama is running and the selected model is installed:

```bash
ollama pull llama3
```

### 3. Start the FastAPI backend

From the project root:

```bash
cd .\Smart-AI-Code-Studio-Improved
dir
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

API documentation:

```text
http://127.0.0.1:8001
```

### 4. Start the Streamlit frontend

Open a second terminal:

```bash
cd .\Smart-AI-Code-Studio-Improved
streamlit run app.py
```

The UI normally opens at:

```text
http://localhost:8501
```

## API endpoints

### `GET /api/health`

Checks the backend and Ollama/model availability.

### `POST /api/analyze`

Runs static code analysis.

Example request:

```json
{
  "code": "def add(a,b): return a+b",
  "language": "Python"
}
```

### `POST /api/validate`

Runs the safety layer and code validation/compilation.

### `POST /api/refactor`

Runs the complete GenAI pipeline:

```text
Analyze
→ LLM Refactor
→ Safety Check
→ Validate
→ Error Feedback
→ Auto-Fix
→ Validate Again
→ Diff + Quality Report
```

## Important safety note

The safety scanner is a **static blocking layer, not a secure sandbox**. Do not execute untrusted code on a machine containing sensitive data. The project is intended as a learning/prototype application.

## Interview explanation

> Smart AI Code Studio is a local LLM-based automated code refactoring system. Streamlit provides the frontend, while FastAPI exposes REST APIs for the backend. The backend performs static analysis and sends a structured refactoring request to a locally hosted Llama 3 model through Ollama. Generated code is passed through a safety check and validation stage. If compilation or execution fails, the error is captured and fed back to the LLM, which attempts to correct the code for a limited number of iterations. After successful validation, the system returns the final code along with a before/after diff, quality metrics, safety information and validation history.

## Validation and Login

The backend also contains a separate legacy validation/refactor pipeline. Do not confuse it with **Run Code**: the Run Code button calls the report-only `/api/diagnose` endpoint and does not execute or modify source. The separate validation/refactor workflow may compile or run generated code as part of its own validation cycle.

1. Python/Java/C++/JavaScript syntax and compiler checks where the local compiler/parser is installed.
2. Optional Pyflakes checks for Python semantic/lint issues, plus a local Qwen2.5-Coder review for undefined names, obvious type/API misuse, and logic concerns.
3. Duplicate issue normalization and explicit report-only guarantees for the Run Code endpoint.

AI review cannot prove arbitrary business logic without tests or a precise specification, so the system reports obvious logic concerns rather than claiming perfect correctness.

### Multi-user login

The Streamlit app now has a local login page. Users are stored in `users.json` using salted PBKDF2 password hashes.

Demo accounts included for local testing:

- `saniya` / `saniya123`
- `admin` / `admin123`

For another local user, run:

```powershell
python manage_users.py
```

For a public/production deployment, replace this demo authentication with a proper identity provider or database-backed authentication and change the demo passwords.

## Run Code diagnostics (improved)

The **Run Code** action is report-only: it never executes or edits submitted source. It uses Python AST parsing, optional Pyflakes semantic/lint checks, Java `javac` when installed, C++ `g++ -fsyntax-only` when installed, and JavaScript `node --check` when installed. It adds conservative, explicit heuristics for common missing-token, indentation, typo, and logic patterns and uses the configured local Ollama model as a second-opinion reviewer when available. Duplicate/near-duplicate issues are normalized and collapsed. Compiler checks are skipped with a partial-check note if the relevant compiler/runtime is not installed.

Logic analysis is necessarily best-effort. For stronger verification, enter the expected behavior/output in the optional field and provide representative test cases. No tool can guarantee detection of every bug from source alone. This feature intentionally does not execute user code during Run Code.

### Start on Windows

Open PowerShell in the folder that contains both `app.py` and the `backend` folder.

Terminal 1:
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Terminal 2, in the same folder:
```powershell
python -m streamlit run app.py
```

Open `http://localhost:8501`. Install Python dependencies with `python -m pip install -r requirements.txt`. Ollama and the selected model (`qwen2.5-coder:7b` by default) are optional for static checks, but needed for AI logic review and refactoring.

### Tests

Run `python -m pytest -q`. The included tests cover core utilities, common syntax/indentation errors, logic checks, duplicate suppression at the API layer, report-only behavior, and the `expected_behavior` refactoring regression.
