"""views/profile.py — Deep candidate profile page."""
import streamlit as st
from utils.state import get_ranked
from utils.ui_components import section_header, mini_bar, empty_state

DECISION_COLORS = {
    "Strong Hire": "#43E97B", "Hire": "#6C63FF",
    "Maybe": "#FFD700", "Weak Maybe": "#FF9944",
    "Not Recommended": "#FF6B6B", "Pending": "#8888A8",
}


def get_name(c):
    return (c.get("scores") or {}).get("name") or c["filename"].replace(".pdf", "")


def safe_ai(c):
    return c.get("ai") or {}


def show():
    section_header("Candidate Profile", "Comprehensive AI-generated profile for individual candidates")

    ranked = get_ranked()
    if not ranked:
        empty_state("👤", "No Candidates", "Analyze CVs first to view profiles.")
        return

    names = [get_name(c) for c in ranked]
    presel    = st.session_state.get("selected_filename", "")
    filenames = [c["filename"] for c in ranked]
    default_idx = filenames.index(presel) if presel in filenames else 0

    idx = st.selectbox("Select Candidate", range(len(names)),
                       format_func=lambda i: names[i],
                       index=default_idx)
    st.session_state["selected_filename"] = ranked[idx]["filename"]

    c  = ranked[idx]
    sc = c["scores"]
    ai = safe_ai(c)
    jd = st.session_state.get("job_description", "")

    name   = get_name(c)
    title  = ai.get("current_title", "")
    score  = sc.get("overall_score", 0)
    dec    = sc.get("decision", "Pending")
    conf   = sc.get("confidence", "")
    col_fg = DECISION_COLORS.get(dec, "#8888A8")
    sc_col = "#43E97B" if score >= 75 else ("#FFD700" if score >= 55 else "#FF6B6B")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Hero Card ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#16162A 0%,#1C1C38 100%);
                border:1px solid #2E2E50; border-radius:18px; padding:28px; margin-bottom:24px;'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start;
                    flex-wrap:wrap; gap:20px;'>
            <div style='flex:1; min-width:200px;'>
                <div style='font-size:1.5rem; font-weight:800; color:#E8E8F8;'>{name}</div>
                <div style='color:#8888A8; font-size:0.88rem; margin-top:4px;'>
                    {title or "—"}
                    {"&nbsp;·&nbsp;" + str(sc.get("experience_years","?")) + " yrs experience"
                     if sc.get("experience_years") else ""}
                </div>
                <div style='color:#8888A8; font-size:0.85rem; margin-top:2px;'>
                    Education: <span style='color:#C0C0D8;'>{sc.get("education_level","Not Specified")}</span>
                    &nbsp;·&nbsp; Seniority: <span style='color:#C0C0D8;'>{sc.get("seniority","Unknown")}</span>
                </div>
                <div style='margin-top:14px; color:#B0B0D0; font-size:0.88rem; line-height:1.65;'>
                    {ai.get("summary","No AI summary — add GROQ_API_KEY and re-analyze.")}
                </div>
            </div>
            <div style='text-align:center; flex-shrink:0;'>
                <div style='font-family:monospace; font-size:3rem; font-weight:800;
                            color:{sc_col}; line-height:1;'>{score}</div>
                <div style='color:#6060A0; font-size:0.75rem; margin-bottom:10px;'>out of 100</div>
                <div style='background:rgba(0,0,0,0.2); border:1px solid {col_fg}50;
                            border-radius:100px; padding:6px 18px; font-weight:700;
                            font-size:0.9rem; color:{col_fg};'>{dec}</div>
                {f"<div style='color:#6060A0; font-size:0.72rem; margin-top:6px;'>Confidence: {conf}</div>" if conf else ""}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score Breakdown ───────────────────────────────────────────────────────
    st.markdown("#### 📊 Score Breakdown")
    gc1, gc2, gc3, gc4 = st.columns(4)
    for col, (label, key) in zip(
        [gc1, gc2, gc3, gc4],
        [("Skills","skills_score"),("Experience","experience_score"),
         ("ATS","ats_score"),("Education","education_score")]
    ):
        v = sc.get(key, 0)
        c_val = "#43E97B" if v >= 75 else ("#FFD700" if v >= 55 else "#FF6B6B")
        with col:
            st.markdown(f"""
            <div style='background:#16162A; border:1px solid #252545; border-radius:12px;
                        padding:16px; text-align:center; margin-bottom:12px;'>
                <div style='font-family:monospace; font-size:1.7rem; font-weight:800; color:{c_val};'>{v}</div>
                <div style='color:#8888A8; font-size:0.72rem; text-transform:uppercase;
                            letter-spacing:0.1em; margin-top:2px;'>{label}</div>
            </div>""", unsafe_allow_html=True)

    # ── Three Columns ─────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("""<div style='background:#16162A; border:1px solid #252545;
            border-radius:12px; padding:18px;'>
            <div class='cf-label' style='margin-bottom:10px;'>✅ Strengths</div>""",
                    unsafe_allow_html=True)
        for s in ai.get("strengths", []) or ["Add GROQ_API_KEY to see AI strengths"]:
            st.markdown(f"""
            <div style='background:rgba(67,233,123,0.07); border:1px solid rgba(67,233,123,0.18);
                border-radius:8px; padding:8px 12px; margin:5px 0; font-size:0.83rem; color:#B0F0C8;'>
                {s}</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("""<div style='background:#16162A; border:1px solid #252545;
            border-radius:12px; padding:18px;'>
            <div class='cf-label' style='margin-bottom:10px;'>⚠️ Concerns</div>""",
                    unsafe_allow_html=True)
        concerns = ai.get("concerns", []) or sc.get("risk_flags", []) or ["None identified"]
        for s in concerns:
            st.markdown(f"""
            <div style='background:rgba(255,107,107,0.07); border:1px solid rgba(255,107,107,0.18);
                border-radius:8px; padding:8px 12px; margin:5px 0; font-size:0.83rem; color:#FFB0B0;'>
                {s}</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_c:
        st.markdown("""<div style='background:#16162A; border:1px solid #252545;
            border-radius:12px; padding:18px;'>
            <div class='cf-label' style='margin-bottom:10px;'>🤝 Culture Fit</div>""",
                    unsafe_allow_html=True)
        for s in ai.get("culture_fit_indicators", []) or ["Add GROQ_API_KEY to see culture fit"]:
            st.markdown(f"""
            <div style='background:rgba(108,99,255,0.07); border:1px solid rgba(108,99,255,0.18);
                border-radius:8px; padding:8px 12px; margin:5px 0; font-size:0.83rem; color:#B0A8FF;'>
                {s}</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Skills ────────────────────────────────────────────────────────────────
    st.markdown("#### 🎯 Skills Analysis")
    sc1, sc2, sc3 = st.columns(3)

    with sc1:
        matched = sc.get("matched_skills", [])
        total_jd = len(sc.get("jd_skills", []))
        st.markdown(f"<div class='cf-label' style='margin-bottom:8px;'>✅ Matched ({len(matched)}/{total_jd} JD skills)</div>",
                    unsafe_allow_html=True)
        tags = " ".join(
            f"<span style='display:inline-block; background:rgba(108,99,255,0.15); color:#A09AFF; "
            f"border:1px solid rgba(108,99,255,0.3); border-radius:100px; padding:3px 10px; "
            f"font-size:0.78rem; margin:2px;'>{s}</span>"
            for s in matched
        )
        st.markdown(f"<div style='line-height:2.2;'>{tags or 'None'}</div>", unsafe_allow_html=True)

    with sc2:
        missing = sc.get("missing_skills", [])
        st.markdown("<div class='cf-label' style='margin-bottom:8px;'>❌ Missing from JD</div>",
                    unsafe_allow_html=True)
        m_tags = " ".join(
            f"<span style='display:inline-block; background:rgba(255,107,107,0.10); color:#FF9E9E; "
            f"border:1px solid rgba(255,107,107,0.25); border-radius:100px; padding:3px 10px; "
            f"font-size:0.78rem; margin:2px;'>{s}</span>"
            for s in missing
        )
        st.markdown(f"<div style='line-height:2.2;'>{m_tags or 'None missing'}</div>",
                    unsafe_allow_html=True)

    with sc3:
        extra = sc.get("extra_skills", [])
        st.markdown("<div class='cf-label' style='margin-bottom:8px;'>➕ Additional Skills</div>",
                    unsafe_allow_html=True)
        e_tags = " ".join(
            f"<span style='display:inline-block; background:rgba(67,233,123,0.10); color:#80F0A0; "
            f"border:1px solid rgba(67,233,123,0.25); border-radius:100px; padding:3px 10px; "
            f"font-size:0.78rem; margin:2px;'>{s}</span>"
            for s in extra[:12]
        )
        st.markdown(f"<div style='line-height:2.2;'>{e_tags or 'None'}</div>", unsafe_allow_html=True)

    # ── Interview Focus Areas ─────────────────────────────────────────────────
    focus = ai.get("interview_focus_areas", [])
    if focus:
        st.markdown("<br>")
        st.markdown("#### 🎤 Interview Focus Areas")
        cols = st.columns(len(focus))
        for i, area in enumerate(focus):
            with cols[i]:
                st.markdown(f"""
                <div style='background:#16162A; border:1px solid #252545; border-radius:10px;
                            padding:14px; text-align:center;'>
                    <div style='font-size:1.4rem; margin-bottom:6px;'>🎯</div>
                    <div style='font-size:0.83rem; color:#C0C0D8; line-height:1.4;'>{area}</div>
                </div>""", unsafe_allow_html=True)

    # ── Full Report ───────────────────────────────────────────────────────────
    st.markdown("<br>")
    st.markdown("#### 📄 Full Evaluation Report")

    from utils.config import get_groq_key
    if not get_groq_key():
        st.markdown("""
        <div style='background:#1A1400; border:1px solid rgba(255,215,0,0.3);
                    border-radius:10px; padding:14px; color:#C0A000; font-size:0.85rem;'>
            ⚠️ Add GROQ_API_KEY to enable full AI report generation.
        </div>""", unsafe_allow_html=True)
        return

    cache_key = f"report_{c['filename']}"

    if cache_key in st.session_state:
        report_text = st.session_state[cache_key]
        # Clean any markdown artifacts before display
        report_text = report_text.replace("####", "").replace("###", "").replace("##", "").replace("#", "")
        report_text = report_text.replace("<br>", "").strip()
        st.markdown(f"""
        <div style='background:#16162A; border:1px solid #252545; border-radius:12px; padding:24px;
                    line-height:1.8; color:#C8C8E0; font-size:0.9rem; white-space:pre-wrap;'>
{report_text}
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Regenerate Report"):
            del st.session_state[cache_key]
            st.rerun()
    else:
        st.markdown("<div style='color:#8888A8; font-size:0.85rem; margin-bottom:12px;'>Generate a 300-word hiring manager report.</div>",
                    unsafe_allow_html=True)
        if st.button("📄 Generate Full Report"):
            with st.spinner("Writing evaluation report..."):
                try:
                    from utils.ai_engine import generate_candidate_report
                    merged = {**sc, **ai}
                    report = generate_candidate_report(c["text"], jd, merged)
                    # Clean markdown artifacts
                    report = report.replace("####","").replace("###","").replace("##","").replace("#","")
                    report = report.replace("<br>","").strip()
                    st.session_state[cache_key] = report
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
