"""views/dashboard.py — Executive dashboard."""
import streamlit as st
from utils.state import get_ranked, get_analyzed
from utils.ui_components import kpi_card, section_header, mini_bar, empty_state

DECISION_ORDER  = ["Strong Hire", "Hire", "Maybe", "Weak Maybe", "Not Recommended"]
DECISION_COLORS = {
    "Strong Hire": "#43E97B", "Hire": "#6C63FF",
    "Maybe": "#FFD700", "Weak Maybe": "#FF9944", "Not Recommended": "#FF6B6B"
}


def get_name(c):
    sc = c.get("scores") or {}
    return sc.get("name") or c["filename"].replace(".pdf", "")


def safe_ai(c):
    """Always return a dict, never None."""
    return c.get("ai") or {}


def show():
    section_header("Dashboard", "Overview of your active recruitment pipeline")

    ranked   = get_ranked()
    analyzed = get_analyzed()
    n_total  = len(st.session_state.get("candidates", []))
    jd_set   = bool(st.session_state.get("job_description"))

    # ── KPI Row ───────────────────────────────────────────────────────────────
    avg_score = int(
        sum(c["scores"].get("overall_score", 0) for c in analyzed) / max(len(analyzed), 1)
    )
    top_count = sum(1 for c in analyzed if c["scores"].get("overall_score", 0) >= 70)
    strong    = sum(
        1 for c in analyzed
        if safe_ai(c).get("recommendation") in ("Strong Hire", "Hire")
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(kpi_card(n_total,          "CVs Uploaded",      "#6C63FF"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card(len(analyzed),    "Analyzed",          "#43E97B"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card(f"{avg_score}",   "Avg Score",         "#A09AFF", "/100"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card(top_count,        "Score ≥ 70",        "#FFD700"), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card(strong,           "Hire Recommended",  "#43E97B"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not analyzed:
        empty_state("📊", "No Data Yet",
                    "Set up a job description and upload CVs to see your dashboard.")
        _quick_start()
        return

    # ── Charts Row ────────────────────────────────────────────────────────────
    col_chart, col_top = st.columns([2, 3], gap="large")

    with col_chart:
        # Recommendation distribution
        st.markdown("""<div style='background:#16162A; border:1px solid #252545;
            border-radius:14px; padding:20px;'>
            <div class='cf-label' style='margin-bottom:14px;'>Recommendation Distribution</div>""",
            unsafe_allow_html=True)

        counts = {}
        for c in analyzed:
            rec = safe_ai(c).get("recommendation") or c["scores"].get("decision") or "Maybe"
            counts[rec] = counts.get(rec, 0) + 1

        total = sum(counts.values()) or 1
        for dec in DECISION_ORDER:
            n = counts.get(dec, 0)
            pct = int(n / total * 100)
            color = DECISION_COLORS.get(dec, "#8888A8")
            st.markdown(f"""
            <div style='display:flex; align-items:center; gap:10px; margin:7px 0;'>
                <div style='width:115px; color:#9090B0; font-size:0.78rem; flex-shrink:0;'>{dec}</div>
                <div style='flex:1; background:#252545; border-radius:100px; height:7px;'>
                    <div style='background:{color}; width:{pct}%; height:7px; border-radius:100px;'></div>
                </div>
                <div style='width:24px; text-align:right; font-weight:700; font-size:0.8rem; color:{color};'>{n}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Score distribution
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div style='background:#16162A; border:1px solid #252545;
            border-radius:14px; padding:20px;'>
            <div class='cf-label' style='margin-bottom:14px;'>Score Distribution</div>""",
            unsafe_allow_html=True)

        buckets = {"90-100": 0, "75-89": 0, "60-74": 0, "45-59": 0, "<45": 0}
        for c in analyzed:
            s = c["scores"].get("overall_score", 0)
            if   s >= 90: buckets["90-100"] += 1
            elif s >= 75: buckets["75-89"]  += 1
            elif s >= 60: buckets["60-74"]  += 1
            elif s >= 45: buckets["45-59"]  += 1
            else:         buckets["<45"]    += 1

        colors_b = {"90-100":"#43E97B","75-89":"#6C63FF","60-74":"#FFD700",
                    "45-59":"#FF9944","<45":"#FF6B6B"}
        for label, n in buckets.items():
            pct = int(n / total * 100)
            color = colors_b[label]
            st.markdown(f"""
            <div style='display:flex; align-items:center; gap:10px; margin:6px 0;'>
                <div style='width:55px; font-family:monospace; color:#9090B0; font-size:0.75rem;'>{label}</div>
                <div style='flex:1; background:#252545; border-radius:100px; height:6px;'>
                    <div style='background:{color}; width:{pct}%; height:6px; border-radius:100px;'></div>
                </div>
                <div style='width:22px; text-align:right; font-weight:700; font-size:0.78rem; color:{color};'>{n}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_top:
        st.markdown("""<div style='background:#16162A; border:1px solid #252545;
            border-radius:14px; padding:20px;'>
            <div class='cf-label' style='margin-bottom:16px;'>Top Candidates</div>""",
            unsafe_allow_html=True)

        for i, c in enumerate(ranked[:6]):
            sc    = c["scores"]
            ai    = safe_ai(c)
            name  = get_name(c)
            title = ai.get("current_title", "")
            score = sc.get("overall_score", 0)
            dec   = sc.get("decision", "Maybe")
            dec_color = DECISION_COLORS.get(dec, "#8888A8")
            s_col = "#43E97B" if score >= 75 else ("#FFD700" if score >= 55 else "#FF6B6B")

            medal_styles = [
                "background:linear-gradient(135deg,#FFD700,#FFA500)",
                "background:linear-gradient(135deg,#C0C0C0,#999)",
                "background:linear-gradient(135deg,#CD7F32,#A0522D)",
            ]
            medal_style = medal_styles[i] if i < 3 else "background:#252545"

            st.markdown(f"""
            <div style='display:flex; align-items:center; gap:12px; padding:10px 0;
                        border-bottom:1px solid #252545;'>
                <div style='width:28px; height:28px; border-radius:50%; {medal_style};
                            display:flex; align-items:center; justify-content:center;
                            font-weight:800; font-size:0.75rem; color:white; flex-shrink:0;'>{i+1}</div>
                <div style='flex:1; min-width:0;'>
                    <div style='font-weight:700; font-size:0.88rem; white-space:nowrap;
                                overflow:hidden; text-overflow:ellipsis;'>{name}</div>
                    <div style='color:#8888A8; font-size:0.75rem;'>{title or c["filename"]}</div>
                </div>
                <div style='text-align:right; flex-shrink:0;'>
                    <div style='font-family:monospace; font-weight:700; color:{s_col}; font-size:0.95rem;'>{score}</div>
                    <div style='color:{dec_color}; font-size:0.7rem; font-weight:600;'>{dec}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── AI Executive Summary ──────────────────────────────────────────────────
    if len(analyzed) >= 2 and jd_set:
        st.markdown("<br>", unsafe_allow_html=True)

        from utils.config import get_groq_key
        if not get_groq_key():
            st.markdown("""
            <div style='background:#16162A; border:1px solid #252545; border-radius:14px; padding:20px;'>
                <div class='cf-label' style='margin-bottom:8px;'>🤖 AI Executive Summary</div>
                <div style='color:#8888A8; font-size:0.85rem;'>Add GROQ_API_KEY to .env to enable AI summaries.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style='background:#16162A; border:1px solid #252545;
                border-radius:14px; padding:22px;'>
                <div class='cf-label' style='margin-bottom:12px;'>🤖 AI Executive Summary</div>""",
                unsafe_allow_html=True)

            cache_key = f"exec_summary_{len(analyzed)}"
            if cache_key not in st.session_state:
                with st.spinner("Generating executive summary..."):
                    try:
                        from utils.ai_engine import pool_executive_summary
                        pool_data = [
                            {**c["scores"], **safe_ai(c)}
                            for c in ranked[:8]
                        ]
                        st.session_state[cache_key] = pool_executive_summary(
                            pool_data, st.session_state["job_description"]
                        )
                    except Exception as e:
                        st.session_state[cache_key] = f"Could not generate summary: {e}"

            st.markdown(
                f"<p style='line-height:1.7; color:#C0C0D8; margin:0;'>{st.session_state[cache_key]}</p></div>",
                unsafe_allow_html=True)


def _quick_start():
    st.markdown("""
    <div style='background:#16162A; border:1px solid #252545; border-radius:14px;
                padding:28px; margin-top:24px;'>
        <div style='font-weight:800; font-size:1.1rem; margin-bottom:20px;'>🚀 Get Started in 3 Steps</div>
        <div style='display:grid; grid-template-columns:repeat(3,1fr); gap:16px;'>
            <div style='background:#13132A; border-radius:10px; padding:18px; border-left:3px solid #6C63FF;'>
                <div style='font-weight:700; margin-bottom:6px;'>1 · Job Setup</div>
                <div style='color:#8888A8; font-size:0.85rem;'>Paste the job description</div>
            </div>
            <div style='background:#13132A; border-radius:10px; padding:18px; border-left:3px solid #FF6B6B;'>
                <div style='font-weight:700; margin-bottom:6px;'>2 · Upload CVs</div>
                <div style='color:#8888A8; font-size:0.85rem;'>Upload PDF resumes</div>
            </div>
            <div style='background:#13132A; border-radius:10px; padding:18px; border-left:3px solid #43E97B;'>
                <div style='font-weight:700; margin-bottom:6px;'>3 · Review & Hire</div>
                <div style='color:#8888A8; font-size:0.85rem;'>See ranked candidates</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
