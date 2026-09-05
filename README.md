# Smart AI Code Studio

## AI-Powered Automated Code Refactoring & Self-Correction

Smart AI Code Studio is an AI-powered code refactoring application built with **Python, Streamlit, Ollama, and Llama 3**.

The system analyzes source code, generates an improved/refactored version using an LLM, executes the generated code, detects execution errors, and automatically sends those errors back to the LLM for correction. This iterative process continues until the code produces a successful output.

---

## Project Objective

The objective of this project is to automate code refactoring and error correction using Artificial Intelligence, reducing manual debugging effort while improving code quality, readability, and maintainability.

---

## Overview

Traditional code refactoring and debugging require developers to manually identify problems, modify code, execute it, and repeat the process when errors occur.

**Smart AI Code Studio** automates this workflow using an LLM-powered self-correction loop.

### Workflow

```text
User Code
    ↓
Code Analysis
    ↓
LLM Refactoring
    ↓
Refactored Code
    ↓
Code Execution
    ↓
 ┌───────────────┐
 │ Error Found?  │
 └───────┬───────┘
         │
     Yes ↓
 Error sent to LLM
         ↓
 LLM fixes the code
         ↓
 Code executed again
         ↓
      Retest
         │
     No Error
         ↓
    Final Output
```

---

## Key Features

* AI-powered code refactoring
* Automated code analysis
* Code optimization suggestions
* Improved code readability
* Automated code execution
* Runtime error detection
* LLM-based error correction
* Iterative self-correction loop
* Supports multiple programming languages
* Interactive Streamlit interface
* Local LLM execution using Ollama
* Llama 3 integration

---

## Supported Programming Languages

The application currently supports:

* Python
* Java
* C++
* JavaScript

---

## How It Works

### 1. Enter Source Code

The user selects a programming language and provides the source code through the Streamlit interface.

### 2. Code Analysis

The system analyzes the submitted code and extracts basic code-level information such as functions, variables, loops, conditions, and lines of code.

### 3. AI Refactoring

The source code is sent to **Llama 3 through Ollama**, which generates a cleaner and improved version of the code.

### 4. Code Execution

The generated code is automatically executed using the appropriate runtime/compiler.

### 5. Error Detection

If the execution produces an error, the error message is captured by the application.

### 6. Self-Correction

The error information is sent back to the LLM along with the generated code.

The LLM analyzes the error and produces a corrected version.

### 7. Retesting

The corrected code is executed again.

This process continues until the code executes successfully or the correction process reaches its configured limit.

### 8. Final Output

When the code executes successfully, the application displays the final refactored code and execution output.

---

## Technology Stack

| Technology | Purpose                            |
| ---------- | ---------------------------------- |
| Python     | Core application development       |
| Streamlit  | Web interface                      |
| Ollama     | Local LLM runtime                  |
| Llama 3    | AI code analysis and refactoring   |
| Requests   | Communication with Ollama API      |
| Java       | Java code execution                |
| C++ / g++  | C++ code compilation and execution |
| Node.js    | JavaScript execution               |
| Git        | Version control                    |
| GitHub     | Source code management             |

---

## Project Structure

```text
Smart-AI-Code-Studio/
│
├── app.py
├── test_llm.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── venv/
```

> `venv/` is excluded from GitHub using `.gitignore`.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/saniyakhadapkar-2005/Smart-AI-Code-Studio.git
```

### 2. Navigate to the Project

```bash
cd Smart-AI-Code-Studio
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Ollama Setup

This project uses Ollama to run the Llama 3 model locally.

Install Ollama and download the required model:

```bash
ollama pull llama3
```

Make sure the Ollama service is running before starting the application.

You can verify the model using:

```bash
ollama list
```

---

## Run the Application

Start the Streamlit application using:

```bash
python -m streamlit run app.py
```

The application will open in your browser.

---

## LLM Connection Test

The project also includes `test_llm.py` for testing the connection between the application and the locally running Ollama LLM.

Run:

```bash
python test_llm.py
```

---

## Example

### Input

```python
def calculate(a, b):
    result = a + b
    return result

print(calculate(10, 20))
```

### AI Refactoring

The LLM analyzes the code and generates an improved version.

### Execution

The refactored code is executed automatically.

### Error Scenario

If the generated code contains an execution error:

```text
Execution Error
       ↓
Error sent to Llama 3
       ↓
Corrected code generated
       ↓
Code executed again
```

### Successful Output

```text
30
```

---

## Advantages

* Reduces manual refactoring effort
* Automates repetitive debugging
* Improves code readability
* Provides AI-assisted code optimization
* Detects runtime errors automatically
* Uses a self-correction mechanism
* Runs the LLM locally using Ollama
* Provides an interactive developer-friendly interface

---

## Future Enhancements

Possible future improvements include:

* Static code quality scoring
* Multi-file project refactoring
* GitHub repository integration
* Unit test generation
* Code documentation generation
* Support for additional programming languages
* Cloud deployment

---

## Author

**Saniya Khadapkar**

MSc Artificial Intelligence Student

GitHub:
https://github.com/saniyakhadapkar-2005

---

## License

This project is developed for educational and portfolio purposes.


##screenshort

1. 
<img width="1865" height="822" alt="code_output" src="https://github.com/user-attachments/assets/1f2befb2-c130-48c2-ade6-f5d364c564f3" />


2.
<img width="1917" height="892" alt="run_code" src="https://github.com/user-attachments/assets/58d5b15e-2227-4605-ae59-9b73291932dd" />

3.
<img width="1915" height="916" alt="analyze_code" src="https://github.com/user-attachments/assets/e36130b5-e40c-4ad1-97d5-c65d524fc32e" />

4.
<img width="1900" height="817" alt="refactor_code" src="https://github.com/user-attachments/assets/eb445931-d19a-4278-ab45-64bfe3fc9a2c" />




