"""
CareerForge AI v2 — HR Intelligence Platform
"""
import os, sys, importlib.util
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Load API key using robust multi-method loader
from utils.config import get_groq_key
get_groq_key()

st.set_page_config(
    page_title="CareerForge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import GLOBAL_CSS
from utils.state  import init_state, get_analyzed

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
init_state()


def load_page(filename: str):
    path = os.path.join(BASE_DIR, "views", f"{filename}.py")
    spec = importlib.util.spec_from_file_location(filename, path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[filename] = mod
    spec.loader.exec_module(mod)
    mod.show()


NAV_OPTIONS = [
    "🏠 Dashboard",
    "📋 Job Setup",
    "📁 Upload & Analyze",
    "🏆 Candidate Ranking",
    "🔍 Candidate Profile",
    "📊 Comparison",
    "❓ Interview Kit",
]

ROUTES = {
    "Dashboard":         "dashboard",
    "Job Setup":         "job_setup",
    "Upload & Analyze":  "upload_analyze",
    "Candidate Ranking": "ranking",
    "Candidate Profile": "profile",
    "Comparison":        "comparison",
    "Interview Kit":     "interview_kit",
}

# ── Handle programmatic navigation from buttons ───────────────────────────────
if "current_page" in st.session_state and st.session_state["current_page"]:
    forced = st.session_state["current_page"]
    st.session_state["current_page"] = ""   # clear after use
    default_idx = NAV_OPTIONS.index(forced) if forced in NAV_OPTIONS else 0
elif "last_page" in st.session_state and st.session_state["last_page"]:
    default_idx = NAV_OPTIONS.index(st.session_state["last_page"]) if st.session_state["last_page"] in NAV_OPTIONS else 0
else:
    default_idx = 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:24px 16px 20px 16px; border-bottom:1px solid #252545; margin-bottom:12px;'>
        <div style='display:flex; align-items:center; gap:10px;'>
            <div style='width:34px; height:34px; background:linear-gradient(135deg,#6C63FF,#A09AFF);
                        border-radius:9px; display:flex; align-items:center; justify-content:center;
                        font-size:1.1rem;'>⚡</div>
            <div>
                <div style='font-weight:800; font-size:1rem; color:#E8E8F8;'>CareerForge</div>
                <div style='color:#6C63FF; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.12em;'>HR Platform</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        NAV_OPTIONS,
        index=default_idx,
        label_visibility="collapsed",
    )

    analyzed = get_analyzed()
    n_total  = len(st.session_state.get("candidates", []))
    jd_ok    = bool(st.session_state.get("job_description"))

    st.markdown(f"""
    <div style='position:absolute; bottom:20px; left:16px; right:16px;'>
        <div style='background:#13132A; border:1px solid #252545; border-radius:10px; padding:14px;'>
            <div style='color:#6060A0; font-size:0.68rem; text-transform:uppercase;
                        letter-spacing:0.1em; margin-bottom:10px;'>Current Session</div>
            <div style='display:flex; flex-direction:column; gap:6px; font-size:0.82rem;'>
                <div style='display:flex; justify-content:space-between;'>
                    <span style='color:#8888A8;'>Job</span>
                    <span style='color:{"#43E97B" if jd_ok else "#FF6B6B"}; font-weight:600;'>
                        {"✓ Set" if jd_ok else "Not set"}</span>
                </div>
                <div style='display:flex; justify-content:space-between;'>
                    <span style='color:#8888A8;'>CVs</span>
                    <span style='color:#A09AFF; font-weight:600;'>{n_total}</span>
                </div>
                <div style='display:flex; justify-content:space-between;'>
                    <span style='color:#8888A8;'>Analyzed</span>
                    <span style='color:#43E97B; font-weight:600;'>{len(analyzed)}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Routing ───────────────────────────────────────────────────────────────────
# Remember last page for rerun persistence
st.session_state["last_page"] = page

page_key = page.split(" ", 1)[1].strip()

if page_key in ROUTES:
    load_page(ROUTES[page_key])
