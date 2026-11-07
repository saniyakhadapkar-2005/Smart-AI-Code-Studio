# Smart AI Code Studio 🚀

### AI-Powered Code Analysis, Validation & Refactoring Platform

Smart AI Code Studio is an AI-powered coding assistant designed to help developers write, validate, analyze, and improve their code using Large Language Models (LLMs).

The application combines a Streamlit frontend with a FastAPI backend and locally hosted AI models through Ollama, providing an AI-assisted coding environment.

## 🌟 Key Features

- **Code Execution:** Run code and view execution results.
- **Code Validation:** Identify syntax errors and coding issues.
- **AI Code Analysis:** Analyze code and understand potential problems.
- **AI Code Refactoring:** Improve code readability, structure, and maintainability.
- **Multi-Language Support:** Work with supported programming languages.
- **Local LLM Integration:** Use Ollama to run AI models locally.
- **FastAPI Backend:** Handle backend processing and API communication.
- **Interactive UI:** Simple and user-friendly Streamlit interface.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Frontend user interface |
| FastAPI | Backend API development |
| Ollama | Local LLM integration |
| Llama 3 | AI-powered code assistance |
| Qwen 2.5 Coder | Code-focused AI model |
| REST API | Frontend-backend communication |
| Git & GitHub | Version control |

## 🏗️ System Architecture

```text
       User
        |
        v
  Streamlit Frontend
        |
        v
   FastAPI Backend
        |
        v
   Code Processing
        |
   +----+-----+
   |          |
   v          v
Validation   Ollama
   |          |
   |       Local LLM
   |          |
   +----+-----+
        |
        v
  Analysis / Refactoring
        |
        v
   Display Results
```

## 📂 Project Structure

```text
Smart-AI-Code-Studio/
│
├── backend/
│   └── main.py
│
├── docs/
│
├── app.py
├── auth.py
├── code_engine.py
├── llm_service.py
├── refactor_engine.py
├── manage_users.py
├── check_login.py
│
├── requirements.txt
├── start_backend.bat
├── start_frontend.bat
├── README.md
└── .gitignore
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/saniyakhadapkar-2005/Smart-AI-Code-Studio.git
```

### 2. Navigate to the Project

```bash
cd Smart-AI-Code-Studio
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate Virtual Environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Install and Start Ollama

Download Ollama:

https://ollama.com/

Pull the required AI models:

```bash
ollama pull llama3
ollama pull qwen2.5-coder:7b
```

Make sure Ollama is running locally.

### 7. Start the Backend

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 8. Start the Frontend

Open another terminal, activate the virtual environment, and run:

```bash
python -m streamlit run app.py
```

## 🔄 Application Workflow

1. User opens the Smart AI Code Studio application.
2. User selects a programming language and provides code.
3. The backend receives the request through FastAPI.
4. The code engine processes the submitted code.
5. Validation identifies possible coding issues.
6. Ollama-powered AI models assist with code analysis and refactoring.
7. Results are displayed through the Streamlit interface.

## 🎯 Project Objectives

- Simplify code validation and analysis.
- Reduce manual effort in identifying coding issues.
- Improve code readability and maintainability.
- Explore practical applications of Generative AI and LLMs.
- Build a local-first AI-powered development assistant.

## 🔮 Future Enhancements

- Support for additional programming languages.
- Advanced logical error detection.
- Improved AI-powered debugging.
- Automated unit test generation.
- Enhanced code optimization.
- Cloud deployment and remote accessibility.

## 👩‍💻 Developer

**Saniya Khadapkar**

MSc Artificial Intelligence Student

GitHub: https://github.com/saniyakhadapkar-2005

---

⭐ If you find this project interesting, feel free to explore the repository!

**Built with Python, FastAPI, Streamlit and Generative AI.**
