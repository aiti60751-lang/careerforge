"""views/ranking.py — Candidate leaderboard."""
import streamlit as st
from utils.state import get_ranked
from utils.ui_components import section_header, empty_state

DECISION_COLORS = {
    "Strong Hire":     "#43E97B",
    "Hire":            "#6C63FF",
    "Maybe":           "#FFD700",
    "Weak Maybe":      "#FF9944",
    "Not Recommended": "#FF6B6B",
    "Pending":         "#8888A8",
}


def get_name(c):
    return (c.get("scores") or {}).get("name") or c["filename"].replace(".pdf", "")


def show():
    section_header("Candidate Ranking", "All candidates ranked by match score")

    ranked = get_ranked()
    if not ranked:
        empty_state("🏆", "No Ranked Candidates", "Upload CVs and run analysis first.")
        return

    # ── Filters ───────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_dec = st.multiselect(
            "Recommendation",
            ["Strong Hire","Hire","Maybe","Weak Maybe","Not Recommended"],
            default=["Strong Hire","Hire","Maybe","Weak Maybe","Not Recommended"],
        )
    with col2:
        min_score = st.slider("Minimum Score", 0, 100, 0, 5)
    with col3:
        sort_by = st.selectbox("Sort By",
            ["Overall Score","Skills Score","Experience","Education"])

    sort_map = {"Overall Score":"overall_score","Skills Score":"skills_score",
                "Experience":"experience_score","Education":"education_score"}
    sort_key = sort_map[sort_by]

    filtered = [
        c for c in ranked
        if c["scores"].get("decision","Pending") in filter_dec
        and c["scores"].get("overall_score", 0) >= min_score
    ]
    filtered.sort(key=lambda c: c["scores"].get(sort_key, 0), reverse=True)

    st.markdown(
        f"<p style='color:#8888A8; font-size:0.85rem; margin:8px 0 16px 0;'>"
        f"Showing <b style='color:#E8E8F8;'>{len(filtered)}</b> of {len(ranked)} candidates</p>",
        unsafe_allow_html=True)

    if not filtered:
        empty_state("🔍", "No Matches", "Try adjusting the filters.")
        return

    medals = {0:"🥇", 1:"🥈", 2:"🥉"}

    for rank_idx, c in enumerate(filtered):
        sc      = c["scores"]
        ai      = c.get("ai") or {}
        name    = get_name(c)
        title   = ai.get("current_title","")
        score   = sc.get("overall_score", 0)
        dec     = sc.get("decision","Pending")
        summary = ai.get("summary","")
        medal   = medals.get(rank_idx, f"#{rank_idx+1}")

        col_fg = DECISION_COLORS.get(dec, "#8888A8")
        sc_col = "#43E97B" if score>=75 else ("#FFD700" if score>=55 else "#FF6B6B")
        exp_str = f" · {sc.get('experience_years','?')} yrs" if sc.get("experience_years") else ""
        edu_str = f" · {sc.get('education_level','')}" if sc.get("education_level","Not Specified") != "Not Specified" else ""

        # ── Card Top ─────────────────────────────────────────────────────────
        st.markdown(f"""
<div style='background:#16162A; border:1px solid #2A2A45;
            border-left:4px solid {col_fg}; border-radius:12px 12px 0 0;
            padding:18px 20px 14px 20px; margin-top:8px;'>
    <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
        <div>
            <div style='font-size:1.05rem; font-weight:800; color:#EEEEFF; margin-bottom:4px;'>
                {medal}&nbsp;&nbsp;{name}
            </div>
            <div style='color:#8888A8; font-size:0.8rem;'>
                {title or c["filename"]}{exp_str}{edu_str}
            </div>
        </div>
        <div style='text-align:right; flex-shrink:0; margin-left:20px;'>
            <div style='font-family:monospace; font-size:2rem; font-weight:800;
                        color:{sc_col}; line-height:1;'>
                {score}<span style='font-size:0.75rem; color:#555580;'>/100</span>
            </div>
            <div style='color:{col_fg}; font-weight:700; font-size:0.78rem; margin-top:4px;'>
                {dec}
            </div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

        # ── Summary ───────────────────────────────────────────────────────────
        if summary:
            st.markdown(f"""
<div style='background:#13132A; border-left:4px solid {col_fg};
            border-right:1px solid #2A2A45; border-bottom:1px solid #2A2A45;
            padding:10px 20px;'>
    <p style='color:#B0B0D0; font-size:0.85rem; line-height:1.6; margin:0;'>{summary}</p>
</div>""", unsafe_allow_html=True)

        # ── Score Bars using st.columns ───────────────────────────────────────
        bars_data = [
            ("Skills",     sc.get("skills_score", 0)),
            ("Experience", sc.get("experience_score", 0)),
            ("ATS",        sc.get("ats_score", 0)),
            ("Education",  sc.get("education_score", 0)),
        ]

        bar_cols = st.columns(4)
        for col, (label, val) in zip(bar_cols, bars_data):
            c_bar = "#43E97B" if val>=75 else ("#FFD700" if val>=55 else "#FF6B6B")
            with col:
                st.markdown(f"""
<div style='background:#13132A; border-left:4px solid {col_fg if label=="Skills" else "transparent"};
            border-right:1px solid #2A2A45; border-bottom:1px solid #2A2A45; padding:10px 14px;'>
    <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
        <span style='color:#777799; font-size:0.72rem;'>{label}</span>
        <span style='color:{c_bar}; font-weight:800; font-size:0.8rem;'>{val}</span>
    </div>
    <div style='background:#252545; border-radius:100px; height:5px;'>
        <div style='background:{c_bar}; width:{val}%; height:5px; border-radius:100px;'></div>
    </div>
</div>""", unsafe_allow_html=True)

        # ── Skills & Flags ────────────────────────────────────────────────────
        matched = sc.get("matched_skills", [])
        missing = sc.get("missing_skills", [])
        flags   = sc.get("risk_flags", [])
        reason  = ai.get("recommendation_reason","")

        bottom_parts = []

        if matched:
            tags = "".join(
                f"<span style='display:inline-block; background:rgba(108,99,255,0.18); "
                f"color:#C0BCFF; border-radius:100px; padding:2px 9px; "
                f"font-size:0.73rem; margin:2px;'>{s}</span>"
                for s in matched[:10])
            bottom_parts.append(
                f"<div style='margin-bottom:6px;'>"
                f"<span style='color:#666688; font-size:0.7rem; text-transform:uppercase; "
                f"letter-spacing:0.08em; margin-right:6px;'>✅ Matched</span>{tags}</div>")

        if missing:
            m_tags = "".join(
                f"<span style='display:inline-block; background:rgba(255,107,107,0.12); "
                f"color:#FF9E9E; border-radius:100px; padding:2px 9px; "
                f"font-size:0.73rem; margin:2px;'>{s}</span>"
                for s in missing[:8])
            bottom_parts.append(
                f"<div style='margin-bottom:6px;'>"
                f"<span style='color:#666688; font-size:0.7rem; text-transform:uppercase; "
                f"letter-spacing:0.08em; margin-right:6px;'>❌ Missing</span>{m_tags}</div>")

        if flags:
            flag_html = " &nbsp; ".join(
                f"<span style='color:#FF9E9E; font-size:0.78rem;'>🚩 {f}</span>"
                for f in flags)
            bottom_parts.append(f"<div style='margin-bottom:4px;'>{flag_html}</div>")

        if reason:
            bottom_parts.append(
                f"<div style='background:#0E0E1E; border-left:3px solid {col_fg}; "
                f"border-radius:0 6px 6px 0; padding:8px 12px; margin-top:6px;'>"
                f"<span style='color:#A0A0C0; font-size:0.8rem;'><b>AI:</b> {reason}</span></div>")

        bottom_html = "".join(bottom_parts)
        st.markdown(f"""
<div style='background:#13132A; border-left:4px solid {col_fg};
            border-right:1px solid #2A2A45; border-bottom:1px solid #2A2A45;
            border-radius:0 0 12px 12px; padding:12px 20px;'>
    {bottom_html if bottom_html else "<span style='color:#555577; font-size:0.8rem;'>No additional info</span>"}
</div>""", unsafe_allow_html=True)

        # ── Action Buttons ────────────────────────────────────────────────────
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        b1, b2, b3, _ = st.columns([1, 1, 1, 3])

        with b1:
            if st.button("🔍 Profile", key=f"prof_{rank_idx}", use_container_width=True):
                st.session_state["selected_filename"] = c["filename"]
                st.session_state["current_page"] = "🔍 Candidate Profile"
                st.rerun()
        with b2:
            if st.button("❓ Interview", key=f"iq_{rank_idx}", use_container_width=True):
                st.session_state["selected_filename"] = c["filename"]
                st.session_state["current_page"] = "❓ Interview Kit"
                st.rerun()
        with b3:
            comp_ids = st.session_state.get("comparison_ids", [])
            in_comp  = c["filename"] in comp_ids
            label    = "✓ In Compare" if in_comp else "📊 Compare"
            if st.button(label, key=f"cmp_{rank_idx}", use_container_width=True):
                if in_comp:
                    comp_ids.remove(c["filename"])
                    st.session_state["comparison_ids"] = comp_ids
                    st.rerun()
                else:
                    if len(comp_ids) < 4:
                        comp_ids.append(c["filename"])
                        st.session_state["comparison_ids"] = comp_ids
                        if len(comp_ids) >= 2:
                            st.session_state["current_page"] = "📊 Comparison"
                        st.rerun()
                    else:
                        st.warning("Max 4 candidates.")

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
