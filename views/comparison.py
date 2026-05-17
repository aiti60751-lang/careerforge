"""views/comparison.py — Side-by-side candidate comparison."""
import streamlit as st
from utils.state import get_ranked
from utils.ui_components import section_header, empty_state

DECISION_COLORS = {
    "Strong Hire": "#43E97B", "Hire": "#6C63FF",
    "Maybe": "#FFD700", "Weak Maybe": "#FF9944",
    "Not Recommended": "#FF6B6B", "Pending": "#8888A8",
}


def get_name(c):
    return (c.get("scores") or {}).get("name") or c["filename"].replace(".pdf", "")


def score_color(val):
    return "#43E97B" if val >= 75 else ("#FFD700" if val >= 55 else "#FF6B6B")


def section_title(icon, title):
    st.markdown(f"""
<div style='background:#1C1C34; border-radius:8px; padding:8px 14px; margin:16px 0 8px 0;'>
    <span style='color:#6C63FF; font-size:0.72rem; font-weight:700;
                 text-transform:uppercase; letter-spacing:0.1em;'>{icon} {title}</span>
</div>""", unsafe_allow_html=True)


def row_label(text):
    st.markdown(
        f"<div style='padding:10px 4px; color:#8888A8; font-size:0.8rem; "
        f"font-weight:600; border-bottom:1px solid #1A1A2E;'>{text}</div>",
        unsafe_allow_html=True)


def show():
    section_header("Comparison", "Compare up to 4 candidates side-by-side")

    ranked = get_ranked()
    if not ranked:
        empty_state("📊", "No Candidates", "Analyze CVs first.")
        return

    all_names = [get_name(c) for c in ranked]
    comp_ids  = st.session_state.get("comparison_ids", [])
    preselected = [get_name(c) for c in ranked if c["filename"] in comp_ids] if comp_ids else all_names[:min(3, len(all_names))]

    selected_names = st.multiselect(
        "Select candidates to compare (2–4)",
        all_names, default=preselected, max_selections=4,
    )

    if len(selected_names) < 2:
        st.info("Select at least 2 candidates to compare.")
        return

    name_to_c = {get_name(c): c for c in ranked}
    selected  = [name_to_c[n] for n in selected_names if n in name_to_c]
    n = len(selected)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    cols = st.columns([1.2] + [2] * n)
    cols[0].markdown("<div style='height:90px;'></div>", unsafe_allow_html=True)

    for i, c in enumerate(selected):
        sc     = c["scores"]
        name   = get_name(c)
        score  = sc.get("overall_score", 0)
        dec    = sc.get("decision", "Pending")
        col_fg = DECISION_COLORS.get(dec, "#8888A8")
        s_col  = score_color(score)
        with cols[i + 1]:
            st.markdown(f"""
<div style='background:#16162A; border:1px solid #2A2A45;
            border-top:3px solid {col_fg}; border-radius:10px;
            padding:14px; text-align:center; margin-bottom:8px;'>
    <div style='font-weight:800; font-size:0.9rem; color:#EEEEFF; margin-bottom:6px;'>{name}</div>
    <div style='font-family:monospace; font-size:1.5rem; font-weight:800; color:{s_col};'>
        {score}<span style='font-size:0.7rem; color:#555580;'>/100</span>
    </div>
    <div style='color:{col_fg}; font-weight:700; font-size:0.75rem; margin-top:4px;'>{dec}</div>
</div>""", unsafe_allow_html=True)

    # ── Scores Section ────────────────────────────────────────────────────────
    section_title("📊", "Scores")

    score_rows = [
        ("Overall Score",  "overall_score"),
        ("Skills Match",   "skills_score"),
        ("Experience",     "experience_score"),
        ("ATS Score",      "ats_score"),
        ("Education",      "education_score"),
    ]

    for label, key in score_rows:
        vals = [c["scores"].get(key, 0) for c in selected]
        best = max(vals)
        cols = st.columns([1.2] + [2] * n)
        with cols[0]:
            row_label(label)
        for i, (c, val) in enumerate(zip(selected, vals)):
            is_best = (val == best and best > 0)
            c_val   = score_color(val)
            with cols[i + 1]:
                star = " ★" if is_best else ""
                st.markdown(
                    f"<div style='padding:4px 8px; font-family:monospace; font-weight:800; "
                    f"color:{c_val}; font-size:1rem; border-bottom:1px solid #1A1A2E;'>"
                    f"{val}/100{star}</div>",
                    unsafe_allow_html=True)
                st.progress(val / 100)

    # ── Profile Section ───────────────────────────────────────────────────────
    section_title("👤", "Profile")

    profile_rows = [
        ("Experience",    lambda c: f"{c['scores'].get('experience_years','?')} yrs"),
        ("Education",     lambda c: c["scores"].get("education_level", "?")),
        ("Seniority",     lambda c: c["scores"].get("seniority", "?")),
        ("Current Title", lambda c: (c.get("ai") or {}).get("current_title", "?")),
    ]

    for label, getter in profile_rows:
        cols = st.columns([1.2] + [2] * n)
        with cols[0]:
            row_label(label)
        for i, c in enumerate(selected):
            with cols[i + 1]:
                st.markdown(
                    f"<div style='padding:10px 8px; color:#C0C0D8; font-size:0.85rem; "
                    f"border-bottom:1px solid #1A1A2E;'>{getter(c) or '—'}</div>",
                    unsafe_allow_html=True)

    # ── Skills Section ────────────────────────────────────────────────────────
    section_title("🎯", "Skills")

    for skill_label, skill_key, color in [
        ("✅ Matched", "matched_skills",  "rgba(108,99,255,0.15)"),
        ("❌ Missing", "missing_skills",   "rgba(255,107,107,0.12)"),
    ]:
        cols = st.columns([1.2] + [2] * n)
        with cols[0]:
            row_label(skill_label)
        for i, c in enumerate(selected):
            skills = c["scores"].get(skill_key, [])[:8]
            tag_color = "#C0BCFF" if "Matched" in skill_label else "#FF9E9E"
            with cols[i + 1]:
                if skills:
                    tags = " ".join(
                        f"<span style='display:inline-block; background:{color}; "
                        f"color:{tag_color}; border-radius:100px; padding:2px 8px; "
                        f"font-size:0.72rem; margin:2px;'>{s}</span>"
                        for s in skills)
                    st.markdown(f"<div style='padding:6px 4px; line-height:2;'>{tags}</div>",
                                unsafe_allow_html=True)
                else:
                    st.markdown("<div style='padding:10px 8px; color:#555577;'>—</div>",
                                unsafe_allow_html=True)

    # ── Risk Flags ────────────────────────────────────────────────────────────
    section_title("🚩", "Risk Flags")

    cols = st.columns([1.2] + [2] * n)
    with cols[0]:
        row_label("Flags")
    for i, c in enumerate(selected):
        flags = c["scores"].get("risk_flags", [])
        with cols[i + 1]:
            if flags:
                for f in flags:
                    st.markdown(
                        f"<div style='color:#FF9E9E; font-size:0.78rem; padding:3px 4px;'>🚩 {f}</div>",
                        unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div style='color:#43E97B; font-size:0.82rem; padding:6px 4px;'>✅ No flags</div>",
                    unsafe_allow_html=True)

    # ── AI Summary ────────────────────────────────────────────────────────────
    section_title("🤖", "AI Summary")

    cols = st.columns([1.2] + [2] * n)
    with cols[0]:
        row_label("Summary")
    for i, c in enumerate(selected):
        summary = (c.get("ai") or {}).get("summary") or "—"
        with cols[i + 1]:
            st.markdown(
                f"<div style='padding:8px 4px; color:#B0B0D0; font-size:0.82rem; line-height:1.55;'>{summary}</div>",
                unsafe_allow_html=True)

    # ── Winner ────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    best      = max(selected, key=lambda c: c["scores"].get("overall_score", 0))
    best_name = get_name(best)
    best_score= best["scores"].get("overall_score", 0)
    best_dec  = best["scores"].get("decision", "")
    best_col  = DECISION_COLORS.get(best_dec, "#43E97B")

    st.markdown(f"""
<div style='background:rgba(67,233,123,0.08); border:1px solid rgba(67,233,123,0.25);
            border-radius:12px; padding:18px 22px;'>
    <span style='font-size:1.5rem;'>🏆</span>
    <span style='font-weight:800; color:#43E97B; font-size:1rem; margin-left:10px;'>
        Top Pick: {best_name}
    </span>
    <span style='color:#8888A8; font-size:0.85rem; margin-left:10px;'>
        {best_score}/100 · <span style='color:{best_col};'>{best_dec}</span>
    </span>
</div>""", unsafe_allow_html=True)
