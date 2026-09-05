import streamlit as st
import io
import sys
import re
import shutil
import requests
import subprocess
import tempfile

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Smart AI Code Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# MODERN SLEEK UI CSS (UPDATED HEADLINE DESIGN)
# ==========================================
st.markdown("""
<style>
/* ---------- 1 · GLOBAL BACKGROUND & STYLING ---------- */
html, body, .stApp {
    background: #090d16 !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.08) 0px, transparent 50%) !important;
    color: #e2e8f0;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.main .block-container {
    padding-top: 1.8rem;
    max-width: 1150px;
}

/* Clear & Glowing Main Title */
.main-title {
    font-size: 48px !important;
    font-weight: 900 !important;
    text-align: center !important;
    color: #ffffff !important;
    letter-spacing: -0.5px !important;
    margin-bottom: 8px !important;
    text-shadow: 0 0 20px rgba(56, 189, 248, 0.6), 0 2px 4px rgba(0, 0, 0, 0.8) !important;
}

.subtitle {
    text-align: center !important;
    color: #cbd5e1 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 30px !important;
}

/* ---------- 2 · SIDEBAR DESIGN ---------- */
section[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}

section[data-testid="stSidebar"] * {
    color: #f1f5f9;
}

/* ---------- 3 · BUTTONS ---------- */
.stButton > button,
[data-testid^="stDownloadButton"] > button {
    width: 100%;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid transparent;
    transition: all 0.2s ease-in-out;
}

/* Run Button - Cyan Glow */
[data-testid="stHorizontalBlock"]:has(.stButton button) > div:nth-child(1) .stButton > button {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);
}

[data-testid="stHorizontalBlock"]:has(.stButton button) > div:nth-child(1) .stButton > button:hover {
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45);
    transform: translateY(-1px);
}

/* Analyze Button - Indigo Glow */
[data-testid="stHorizontalBlock"]:has(.stButton button) > div:nth-child(2) .stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
}

[data-testid="stHorizontalBlock"]:has(.stButton button) > div:nth-child(2) .stButton > button:hover {
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45);
    transform: translateY(-1px);
}

/* Refactor Button - Purple/Pink Glow */
[data-testid="stHorizontalBlock"]:has(.stButton button) > div:nth-child(3) .stButton > button {
    background: linear-gradient(135deg, #9333ea 0%, #c026d3 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(147, 51, 234, 0.25);
}

[data-testid="stHorizontalBlock"]:has(.stButton button) > div:nth-child(3) .stButton > button:hover {
    box-shadow: 0 6px 20px rgba(147, 51, 234, 0.45);
    transform: translateY(-1px);
}

/* ---------- 4 · METRICS CARDS ---------- */
[data-testid="stMetric"] {
    background: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: border 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #38bdf8 !important;
}

[data-testid="stMetricLabel"] p {
    color: #64748b !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
}

[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
    font-size: 26px !important;
    font-weight: 700 !important;
}

/* ---------- 5 · TEXT AREA & CODE CONTAINERS ---------- */
textarea, [data-testid="stTextArea"] textarea {
    background-color: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Fira Code', 'Courier New', monospace !important;
}

textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
}

[data-testid="stCode"] {
    border-radius: 10px !important;
    border: 1px solid #1e293b !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR CONTROL PANEL
# ==========================================
with st.sidebar:
    st.title("⚙️ Control Panel")
    theme = st.toggle("🌙 Dark Mode", value=True)
    language = st.selectbox(
        "💻 Select Language",
        ["Python", "Java", "C++", "JavaScript"]
    )

# ==========================================
# TITLE SECTION
# ==========================================
st.markdown('<div class="main-title">🚀 Smart AI Code Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Next-Gen AI Automated Code Refactoring & Analysis Platform</div>', unsafe_allow_html=True)

# ==========================================
# FILE UPLOAD & CODE INPUT
# ==========================================
uploaded_file = st.file_uploader("📂 Upload Code File", type=["py", "java", "cpp", "js"])

st.subheader("✍️ Code Editor")
default_code = ""
if uploaded_file is not None:
    default_code = uploaded_file.read().decode("utf-8")

code = st.text_area("Write your code below:", value=default_code, height=300)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def clean_code(code):
    if not code:
        return ""
    lines = code.split("\n")
    clean_lines = [line for line in lines if "```" not in line]
    return "\n".join(clean_lines).strip()

def wrap_java_code(code):
    if "class" not in code:
        return f"public class Main {{\n    public static void main(String[] args) {{\n        {code}\n    }}\n}}"
    return code

# ==========================================
# RUN CODE FUNCTION
# ==========================================
def run_code(code, language):
    try:
        code = clean_code(code)
        if language == "Python":
            buffer = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = buffer
            try:
                exec(code, {})
            except Exception as e:
                sys.stdout = old_stdout
                return False, str(e)
            sys.stdout = old_stdout
            output = buffer.getvalue()
            return True, output if output else "No Output"

        elif language == "Java":
            if shutil.which("javac") is None:
                return False, "⚠️ Java compiler (`javac`) was not found on this system."
            code = wrap_java_code(code)
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = f"{temp_dir}/Main.java"
                with open(file_path, "w") as f:
                    f.write(code)
                compile_process = subprocess.run(["javac", file_path], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    return False, compile_process.stderr
                run_process = subprocess.run(["java", "-cp", temp_dir, "Main"], capture_output=True, text=True)
                return True, run_process.stdout

        elif language == "C++":
            if shutil.which("g++") is None:
                return False, "⚠️ C++ compiler (`g++`) was not found on this system."
            with tempfile.TemporaryDirectory() as temp_dir:
                cpp_file = f"{temp_dir}/main.cpp"
                exe_file = f"{temp_dir}/main.exe"
                with open(cpp_file, "w") as f:
                    f.write(code)
                compile_process = subprocess.run(["g++", cpp_file, "-o", exe_file], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    return False, compile_process.stderr
                run_process = subprocess.run([exe_file], capture_output=True, text=True)
                return True, run_process.stdout

        elif language == "JavaScript":
            if shutil.which("node") is None:
                return False, "⚠️ JavaScript runtime (`node`) was not found on this system."
            with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w") as temp_js:
                temp_js.write(code)
                temp_js_path = temp_js.name
            run_process = subprocess.run(["node", temp_js_path], capture_output=True, text=True)
            if run_process.returncode != 0:
                return False, run_process.stderr
            return True, run_process.stdout

    except Exception as e:
        return False, str(e)

# ==========================================
# REGEX CODE ANALYZER
# ==========================================
def analyze_code(code, language):
    is_python = (language or "").lower().startswith("py")
    lines = code.splitlines()
    loc_total = len(lines)
    loc_blank = sum(1 for ln in lines if not ln.strip())
    loc_code = loc_total - loc_blank

    loops = len(re.findall(r"\b(for|while)\b", code))
    functions = len(re.findall(r"\b(def|void|int|String|class|function)\s+\w+", code))
    conditionals = len(re.findall(r"\b(if|elif|else if|switch)\b", code))
    variables = len(re.findall(r"([a-zA-Z_]\w*)\s*=\s*", code))

    return {
        "functions": functions,
        "variables": variables,
        "loops": loops,
        "conditionals": conditionals,
        "loc_total": loc_total,
        "loc_code": loc_code,
        "loc_blank": loc_blank,
        "loc_comment": 0
    }

# ==========================================
# AI REFACTOR (OLLAMA LOCAL LLM)
# ==========================================
def llm_refactor(code, language):
    prompt = f"Fix and optimize this {language} code. Return ONLY clean executable code without any explanations or Markdown formatting:\n"
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt + code, "stream": False},
            timeout=180
        )
        data = res.json()
        clean = clean_code(data.get("response", ""))
        if language == "Java":
            clean = wrap_java_code(clean)
        return clean
    except Exception as e:
        return f"ERROR: {e}"

# ==========================================
# BUTTONS & ACTION HANDLING
# ==========================================
st.divider()
col1, col2, col3 = st.columns(3)

run_btn = col1.button("▶ Run Code")
analyze_btn = col2.button("📊 Analyze Code")
refactor_btn = col3.button("🧠 AI Refactor")
st.divider()

if run_btn and code:
    st.subheader("📤 Output")
    success, result = run_code(code, language)
    if success:
        st.success(result)
    else:
        st.error(result)

if analyze_btn and code:
    st.subheader("📊 Code Analysis")
    m = analyze_code(code, language)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("⚙️ Functions", m["functions"])
    c2.metric("📦 Variables", m["variables"])
    c3.metric("🔁 Loops", m["loops"])
    c4.metric("🔀 Conditionals", m["conditionals"])
    c5.metric("📄 Total LOC", m["loc_total"])

if refactor_btn and code:
    st.subheader("🧠 AI Refactored Code")
    with st.spinner("Generating AI Refactor..."):
        fixed = llm_refactor(code, language)
    st.code(fixed, language=language.lower())
    st.download_button(
        label="📥 Download Refactored Code",
        data=fixed,
        file_name=f"refactored_code.{'py' if language=='Python' else 'txt'}",
        mime="text/plain"
    )