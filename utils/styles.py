"""utils/styles.py — Global CSS injection."""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

/* ── Reset & Base ─────────────────────────────────────────────── */
:root {
    --bg:      #0E0E1A;
    --surface: #13132A;
    --card:    #16162A;
    --card2:   #1C1C34;
    --border:  #252545;
    --border2: #2E2E50;
    --accent:  #6C63FF;
    --accent2: #FF6B6B;
    --accent3: #43E97B;
    --accent4: #FFB443;
    --text:    #E8E8F8;
    --muted:   #8888A8;
    --muted2:  #6060A0;
    --font:    'Plus Jakarta Sans', sans-serif;
    --mono:    'Fira Code', monospace;
}

* { font-family: var(--font) !important; }
code, pre { font-family: var(--mono) !important; }

/* App background */
.stApp { background: var(--bg) !important; color: var(--text) !important; }
.main .block-container { padding: 2rem 2.5rem !important; max-width: 1400px !important; }

/* ── Sidebar ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    width: 240px !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* Sidebar radio as nav */
[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}
[data-testid="stSidebar"] .stRadio > div > label {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 9px 12px !important;
    color: var(--muted) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    cursor: pointer !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: var(--card2) !important;
    color: var(--text) !important;
}
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
    background: rgba(108,99,255,0.15) !important;
    color: var(--accent) !important;
}

/* Hide radio circles */
[data-testid="stSidebar"] .stRadio [type="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio > div > label > div:first-child { display: none !important; }
[data-testid="stSidebar"] .stRadio > div > label > div:last-child {
    margin-left: 0 !important;
}

/* ── Typography ──────────────────────────────────────────────── */
h1 { font-size: 1.8rem !important; font-weight: 800 !important; color: var(--text) !important; letter-spacing: -0.02em !important; }
h2 { font-size: 1.3rem !important; font-weight: 700 !important; color: var(--text) !important; }
h3 { font-size: 1.1rem !important; font-weight: 700 !important; color: var(--text) !important; }
p  { color: #C0C0D8 !important; line-height: 1.65 !important; }

/* ── Buttons ──────────────────────────────────────────────────── */
.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: opacity 0.2s, transform 0.1s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary button (text) */
.btn-secondary > button {
    background: var(--card2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
}

/* ── Inputs ───────────────────────────────────────────────────── */
.stTextArea textarea,
.stTextInput input,
.stNumberInput input {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
}
.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.12) !important;
}

/* ── Selectbox & Multiselect ─────────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

/* ── File uploader ────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 2px dashed var(--border2) !important;
    border-radius: 12px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

/* ── Slider ───────────────────────────────────────────────────── */
.stSlider > div > div > div > div { background: var(--accent) !important; }

/* ── Progress ─────────────────────────────────────────────────── */
.stProgress > div > div { background: var(--accent) !important; border-radius: 100px !important; }
.stProgress > div { background: var(--border) !important; border-radius: 100px !important; }

/* ── Expander ─────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── Tabs ─────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: var(--muted) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 8px 16px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--card2) !important;
    color: var(--text) !important;
}

/* ── Alerts ───────────────────────────────────────────────────── */
.stAlert { border-radius: 10px !important; }

/* ── Divider ──────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 20px 0 !important; }

/* ── Metric ───────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 800 !important; }

/* ── Checkbox ─────────────────────────────────────────────────── */
.stCheckbox > label { color: var(--text) !important; }

/* ── Spinner text ─────────────────────────────────────────────── */
.stSpinner > div > div { border-top-color: var(--accent) !important; }

/* ── Scrollbar ────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 100px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted2); }

/* ── Custom utility classes ───────────────────────────────────── */
.cf-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 12px;
}
.cf-card-hover { transition: border-color 0.2s, transform 0.2s; }
.cf-card-hover:hover { border-color: var(--accent); transform: translateY(-1px); }

.cf-label {
    color: var(--muted);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    margin-bottom: 4px;
}

/* Comparison table */
.compare-table { width: 100%; border-collapse: collapse; }
.compare-table th {
    background: var(--card2);
    color: var(--muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}
.compare-table td {
    padding: 12px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    font-size: 0.88rem;
}
.compare-table tr:hover td { background: rgba(108,99,255,0.04); }

/* Rank medal */
.rank-medal {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.85rem;
}
</style>
"""
