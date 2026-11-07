import requests
import streamlit as st

from code_engine import LANG_EXTENSIONS

API_BASE = "https://smart-ai-code-studio.onrender.com"
DEFAULT_MODEL = "qwen2.5-coder:7b"
DEFAULT_GOAL = "Improve readability, maintainability, efficiency and error handling while preserving intended behavior."

st.set_page_config(
    page_title="Smart AI Code Studio",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Clean, compact UI
# -----------------------------
st.markdown(
    """
<style>
:root {
    --bg:#0b0f17;
    --panel:#111722;
    --panel2:#151c28;
    --border:#273244;
    --muted:#8d99aa;
    --text:#edf2f7;
    --accent:#7c8cff; --pink:#ec4899; --cyan:#22d3ee;
}
.stApp { background:var(--bg); color:var(--text); }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:1180px; padding:1rem 1.2rem 2rem; }
.hero { background:linear-gradient(120deg,rgba(105,120,255,.13),rgba(236,72,153,.10),rgba(34,211,238,.08)); border:1px solid #29334a; border-radius:16px; margin-bottom:.7rem; text-align:center; padding:.15rem 0 .75rem; }
.hero h1 { margin:0; font-size:2rem; font-weight:800; letter-spacing:-.02em; }
.hero p { margin:.2rem 0 0; color:var(--muted); font-size:.8rem; }
.section-title { color:#a5b4fc; margin:.65rem 0 .35rem; font-size:.95rem; font-weight:750; }
.card {
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:10px;
    padding:10px 12px;
}
.result-card {
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:9px;
    padding:9px 11px;
    min-height:64px;
}
.result-label { color:var(--muted); font-size:.7rem; margin-bottom:3px; }
.result-value { font-size:.95rem; font-weight:750; }
.stButton > button { border-radius:9px; font-weight:700; min-height:2.65rem; border:1px solid #39465d; }
.stButton > button[kind="primary"] { background:linear-gradient(90deg,#6978ff,#8b5cf6); border:0; color:white; }
div[data-testid="stAlert"] { border-radius:10px; }
.action-hint { color:var(--muted); font-size:.76rem; margin-top:-.35rem; margin-bottom:.45rem; }
.change-item { background:#121b28; border:1px solid #273244; border-radius:8px; padding:8px 10px; margin:5px 0; }
textarea { font-family:'Fira Code','Consolas','Courier New',monospace !important; }
[data-testid="stSidebar"] { background:#0d121b; }
[data-testid="stSidebar"] .block-container { padding:1rem .85rem; }
[data-testid="stFileUploader"] section { padding:.5rem; }
[data-testid="stDataFrame"] { border-radius:9px; }
.small-note { color:var(--muted); font-size:.72rem; }
.output-title { font-size:.9rem; font-weight:750; margin:.6rem 0 .3rem; }
</style>
""",
    unsafe_allow_html=True,
)


def api_get(path, params=None, timeout=10):
    return requests.get(f"{API_BASE}{path}", params=params, timeout=timeout)


def api_post(path, payload, timeout=60):
    return requests.post(f"{API_BASE}{path}", json=payload, timeout=timeout)


def response_json_or_error(response):
    """Decode JSON safely and provide useful diagnostics for non-JSON API replies."""
    try:
        data = response.json()
        if isinstance(data, dict):
            return data
        return {"detail": str(data)}
    except (requests.exceptions.JSONDecodeError, ValueError):
        snippet = (response.text or "").strip().replace("\n", " ")[:500]
        if not snippet:
            snippet = "The API returned an empty response."
        return {"detail": f"FastAPI returned a non-JSON response (HTTP {response.status_code}): {snippet}"}


def backend_health():
    try:
        response = api_get("/api/health", {"model": DEFAULT_MODEL}, timeout=4)
        data = response_json_or_error(response)
        if response.status_code >= 400 or data.get("backend") != "ok":
            return {"backend": "error", "detail": data.get("detail", f"HTTP {response.status_code}"), "ollama": {"available": False}}
        return data
    except requests.RequestException as exc:
        return {"backend": "offline", "detail": str(exc), "ollama": {"available": False}}


# -----------------------------
# Sidebar — only useful user input
# -----------------------------
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    language = st.selectbox("Language", list(LANG_EXTENSIONS.keys()))
    st.caption("Local AI · FastAPI · Ollama")

health = backend_health()
if health.get("backend") != "ok":
    st.warning(
        "FastAPI backend is not responding correctly. Start it in a separate terminal with "
        "`python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`. "
        + str(health.get("detail", "Check the backend terminal for errors."))
    )

# -----------------------------
# Header
# -----------------------------
st.markdown(
    '<div class="hero"><h1>🚀 Smart AI Code Studio</h1><p>Analyze · Refactor · Auto-Fix</p></div>',
    unsafe_allow_html=True,
)

# -----------------------------
# Source code input
# -----------------------------
st.markdown('<div class="section-title">📄 Source Code</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload source file",
    type=["py", "java", "cpp", "js"],
    label_visibility="collapsed",
)

default_code = ""
if uploaded:
    try:
        default_code = uploaded.getvalue().decode("utf-8")
    except UnicodeDecodeError:
        st.error("Could not decode the uploaded file as UTF-8.")

code = st.text_area(
    "Source Code",
    value=default_code,
    height=245,
    placeholder="Paste your source code here...",
    label_visibility="collapsed",
)

# -----------------------------
# Actions
# -----------------------------
a1, a2, a3 = st.columns([1.4, 1, 1.15])
validate_btn = a1.button("▶️ 1. Run Code", use_container_width=True, type="primary", help="Ask AI to identify code issues. This button reports issues only and does not modify your code.")
analyze_btn = a2.button("📊 2. Analyze Code", use_container_width=True, help="Show code structure metrics and a chart.")
refactor_btn = a3.button("✨ 3. Refactor Code", use_container_width=True, help="Improve code and explain the changes made.")
st.markdown('<div class="action-hint">Recommended order: Run Code → Analyze Code → Refactor Code. Static checks catch syntax and common defects; expected behavior improves logic review.</div>', unsafe_allow_html=True)
expected_behavior = st.text_input("Expected behavior (optional, helps detect logic bugs)", placeholder="Example: For marks = 75, output should be Pass")

# -----------------------------
# Analysis — cards + visualization only
# -----------------------------
if analyze_btn:
    if not code.strip():
        st.warning("Enter code first.")
    elif health.get("backend") != "ok":
        st.error("Start the FastAPI backend first.")
    else:
        try:
            with st.spinner("Analyzing..."):
                response = api_post(
                    "/api/analyze",
                    {"code": code, "language": language},
                    timeout=15,
                )

            if response.status_code >= 400:
                st.error(response_json_or_error(response).get("detail", response.text))
            else:
                metrics = response_json_or_error(response).get("metrics", {})

                st.markdown('<div class="section-title">Code Analysis</div>', unsafe_allow_html=True)
                cols = st.columns(5)
                cards = [
                    ("Functions", metrics.get("functions", 0)),
                    ("Variables", metrics.get("variables", 0)),
                    ("Loops", metrics.get("loops", 0)),
                    ("Complexity", metrics.get("complexity", 0)),
                    ("Code Lines", metrics.get("loc_code", 0)),
                ]
                for col, (label, value) in zip(cols, cards):
                    col.markdown(
                        f'<div class="result-card"><div class="result-label">{label}</div><div class="result-value">{value}</div></div>',
                        unsafe_allow_html=True,
                    )

                # Simple visualization based directly on the analysis cards.
                chart_data = {
                    "Functions": metrics.get("functions", 0),
                    "Variables": metrics.get("variables", 0),
                    "Loops": metrics.get("loops", 0),
                    "Complexity": metrics.get("complexity", 0),
                    "Code Lines": metrics.get("loc_code", 0),
                }
                st.markdown('<div class="section-title">Code Overview</div>', unsafe_allow_html=True)
                st.bar_chart(chart_data, height=220)

        except requests.RequestException as exc:
            st.error(f"FastAPI connection failed: {exc}")

# -----------------------------
# Run Code / Issue Review — report only; never auto-fix or replace source
# -----------------------------
if validate_btn:
    if not code.strip():
        st.warning("Enter code first.")
    elif health.get("backend") != "ok":
        st.error("Start the FastAPI backend first.")
    else:
        try:
            with st.spinner("Checking syntax and asking the AI to review possible logic issues..."):
                response = api_post(
                    "/api/diagnose",
                    {"code": code, "language": language, "model": DEFAULT_MODEL, "expected_behavior": expected_behavior},
                    timeout=240,
                )
            if response.status_code >= 400:
                st.error(response_json_or_error(response).get("detail", response.text))
            else:
                result = response_json_or_error(response)
                issues = result.get("issues", [])
                st.markdown('<div class="section-title">Code Issues</div>', unsafe_allow_html=True)
                if issues:
                    st.warning(f"Found {len(issues)} issue(s) or concern(s). Original code has not been changed.")
                    st.caption(f"Syntax check: {'verified — passed' if result.get('syntax_verified') and result.get('syntax_ok') else 'verified — errors found' if result.get('syntax_verified') else 'partial (compiler/parser unavailable)'} · Code executed: No")
                    for index, issue in enumerate(issues, start=1):
                        st.markdown(f"**{index}.** {issue}")
                else:
                    st.success("No obvious issues detected by the available checks.")
                if result.get("summary"):
                    st.caption(result["summary"])
                if result.get("ai_review") is False:
                    st.info("Static checks ran, but AI logic review was unavailable. Start Ollama and ensure the selected model is installed for logic review.")
                st.info("Run Code only reports issues; it does not execute or modify your source. Logic checks are best-effort; provide expected behavior or tests for stronger verification. Use **3. Refactor Code** to generate improved code.")
        except requests.Timeout:
            st.error("AI issue review timed out. Check Ollama and try again.")
        except requests.RequestException as exc:
            st.error(f"FastAPI connection failed: {exc}")

# -----------------------------
# Refactoring — direct output only
# -----------------------------
if refactor_btn:
    if not code.strip():
        st.warning("Enter code first.")
    elif health.get("backend") != "ok":
        st.error("Start the FastAPI backend first.")
    elif not health.get("ollama", {}).get("available"):
        st.error("Start Ollama first.")
    elif not health.get("ollama", {}).get("model_installed"):
        st.error(f"Model '{DEFAULT_MODEL}' is not installed in Ollama.")
    else:
        try:
            with st.spinner("AI is refactoring and checking the code..."):
                response = api_post(
                    "/api/refactor",
                    {
                        "code": code,
                        "language": language,
                        "goal": DEFAULT_GOAL,
                        "model": DEFAULT_MODEL,
                        "max_attempts": 3,
                        "allow_risky": False,
                    },
                    timeout=300,
                )

            if response.status_code >= 400:
                st.error(response_json_or_error(response).get("detail", response.text))
            else:
                result = response_json_or_error(response)
                after_code = result.get("code", "")
                after_metrics = result.get("after_metrics", {})
                metadata = result.get("metadata", {}) or {}
                original_changed = after_code.strip() != code.strip()

                if result.get("success"):
                    st.success(f"Refactoring complete · validation passed in {result.get('attempts', 1)} attempt(s)")
                else:
                    history = result.get("history", [])
                    last_error = history[-1].get("error", "") if history else "Validation could not be completed."
                    if any(word in last_error.lower() for word in ("compiler", "runtime", "not found")):
                        st.warning("Code was generated, but this language's compiler/runtime is unavailable here. Validation is unconfirmed.")
                    else:
                        st.warning("Code was generated, but some issues remain. Please review before using it.")

                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div class="result-card"><div class="result-label">Validation</div><div class="result-value">{"PASS ✓" if result.get("success") else "UNCONFIRMED ⚠"}</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="result-card"><div class="result-label">Fix attempts</div><div class="result-value">{result.get("attempts", 1)} / 3</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="result-card"><div class="result-label">Safety scan</div><div class="result-value">{after_metrics.get("risk_level", "UNKNOWN")}</div></div>', unsafe_allow_html=True)

                st.markdown('<div class="output-title">Generated code</div>', unsafe_allow_html=True)
                st.code(after_code, language=language.lower())

                # Show both AI's short explanation and a concrete code diff so claims can be checked.
                st.markdown('<div class="output-title">AI explanation of changes</div>', unsafe_allow_html=True)
                summary = metadata.get("summary", "")
                if summary:
                    st.write(summary)
                st.caption("The summary below is generated by the LLM; inspect the exact diff to verify every claimed change.")
                changes = metadata.get("changes", [])
                if changes:
                    for item in changes[:8]:
                        st.markdown(f'<div class="change-item">• {item}</div>', unsafe_allow_html=True)
                else:
                    st.caption("The model did not return a reliable change list. Use the actual diff below to inspect edits.")
                comparison = result.get("comparison", {}) or {}
                st.caption(f"Actual text diff: {comparison.get('added', 0)} line(s) added · {comparison.get('removed', 0)} line(s) removed")
                diff_text = comparison.get("diff", "")
                if diff_text:
                    with st.expander("Exact code diff (original vs generated)", expanded=True):
                        st.code(diff_text, language="diff")
                with st.expander("Compare original code", expanded=False):
                    st.code(code, language=language.lower())

                successful_runs = [h for h in result.get("history", []) if h.get("success") and h.get("output") not in (None, "", "No Output")]
                if successful_runs:
                    st.markdown('<div class="output-title">Program output</div>', unsafe_allow_html=True)
                    st.code(successful_runs[-1].get("output", ""), language="text")

                ext = LANG_EXTENSIONS[language]
                st.download_button("⬇️ Download refactored code", data=after_code, file_name=f"refactored_code.{ext}", mime="text/plain", use_container_width=True)

        except requests.Timeout:
            st.error("The AI request timed out. Check Ollama and try again.")
        except requests.RequestException as exc:
            st.error(f"FastAPI connection failed: {exc}")
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")
