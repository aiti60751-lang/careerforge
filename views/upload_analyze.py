"""views/upload_analyze.py — Bulk CV upload with hybrid analysis."""
import streamlit as st
import os
from utils.state import upsert_candidate
from utils.pdf_reader import extract_text
from utils.scoring_engine import compute_rules_score, make_hiring_decision
from utils.ui_components import section_header


def _extract_name_from_cv(text: str, filename: str) -> str:
    import re
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:8]:
        if any(x in line.lower() for x in ["curriculum","resume","cv","@","http",
                                            "linkedin","phone","tel:","email","address"]):
            continue
        if len(line) > 50 or len(line) < 3:
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
    return filename.replace(".pdf","").replace("_"," ").replace("-"," ").title()


def _run_analysis(candidate: dict, jd: str, weights: dict, use_ai: bool = True):
    text = candidate["text"]
    rules = compute_rules_score(text, jd, weights)
    rules["name"] = _extract_name_from_cv(text, candidate["filename"])
    candidate["scores"] = rules

    from utils.config import get_groq_key
    if use_ai and get_groq_key():
        try:
            from utils.ai_engine import ai_analyze_cv
            ai = ai_analyze_cv(text, jd, rules)
            if ai.get("name") and ai["name"] not in ("Unknown","N/A",""):
                rules["name"] = ai["name"]
            candidate["ai"] = ai
        except Exception as e:
            candidate["ai"] = None
    else:
        candidate["ai"] = None

    decision = make_hiring_decision(rules, candidate.get("ai"))
    candidate["scores"]["decision"]   = decision["decision"]
    candidate["scores"]["confidence"] = decision["confidence"]


def show():
    section_header("Upload & Analyze", "Drop CV files — hybrid Rules + AI analysis")

    if not st.session_state.get("job_description"):
        st.markdown("""
        <div style='background:#1F0D0D; border:1px solid rgba(255,107,107,0.3);
                    border-radius:12px; padding:20px;'>
            ⚠️ <b>Job description not set.</b> Go to <b>Job Setup</b> first.
        </div>""", unsafe_allow_html=True)
        return

    from utils.config import get_groq_key
    jd      = st.session_state["job_description"]
    weights = st.session_state["weights"]
    has_api = bool(get_groq_key())

    # API status
    if not has_api:
        st.markdown("""
        <div style='background:#1A1400; border:1px solid rgba(255,215,0,0.3);
                    border-radius:10px; padding:12px 16px; margin-bottom:16px;'>
            ⚠️ <b style='color:#FFD700;'>No GROQ_API_KEY</b>
            <span style='color:#9090A0; font-size:0.85rem; margin-left:8px;'>
                Rules Engine only — add key to utils/config.py for full AI features.
            </span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#0A1F0A; border:1px solid rgba(67,233,123,0.3);
                    border-radius:10px; padding:12px 16px; margin-bottom:16px;'>
            ✅ <b style='color:#43E97B;'>AI Mode Active</b>
            <span style='color:#9090A0; font-size:0.85rem; margin-left:8px;'>
                Full hybrid Rules + AI analysis enabled.
            </span>
        </div>""", unsafe_allow_html=True)

    # Upload
    uploaded = st.file_uploader(
        "Upload CVs (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded:
        existing  = {c["filename"] for c in st.session_state["candidates"]}
        new_files = [f for f in uploaded if f.name not in existing]

        if new_files:
            st.markdown(f"""
            <div style='background:#0A1F2E; border:1px solid rgba(108,99,255,0.3);
                border-radius:10px; padding:14px; margin:12px 0; color:#A09AFF;'>
                📥 <b>{len(new_files)} new file(s)</b> ready to analyze
            </div>""", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                run_ai = st.checkbox("Include AI Analysis", value=has_api, disabled=not has_api)
            with col_b:
                est = len(new_files) * (8 if (run_ai and has_api) else 1)
                st.markdown(f"<div style='padding-top:8px; color:#8888A8; font-size:0.82rem;'>Est. ~{est}s</div>",
                            unsafe_allow_html=True)

            if st.button(f"🚀 Analyze {len(new_files)} CV(s)"):
                pb = st.progress(0)
                status = st.empty()
                errors = []
                for i, f in enumerate(new_files):
                    status.markdown(
                        f"<div style='color:#A09AFF;'>⏳ Processing <b>{f.name}</b> ({i+1}/{len(new_files)})...</div>",
                        unsafe_allow_html=True)
                    try:
                        text = extract_text(f.read())
                        c = upsert_candidate(f.name, text)
                        _run_analysis(c, jd, weights, use_ai=(run_ai and has_api))
                    except Exception as e:
                        errors.append(f"{f.name}: {e}")
                    pb.progress((i+1)/len(new_files))
                pb.empty()
                msg = f"✅ Done! {len(new_files)-len(errors)} analyzed."
                if errors:
                    msg += f" Errors: {'; '.join(errors)}"
                status.markdown(f"<div style='color:#43E97B; font-weight:600;'>{msg}</div>",
                                unsafe_allow_html=True)
                st.rerun()
        else:
            st.info("All files already loaded.")

    # ── CV Table ──────────────────────────────────────────────────────────────
    candidates = st.session_state.get("candidates", [])
    if not candidates:
        st.markdown("""
        <div style='text-align:center; padding:60px 0; color:#8888A8;'>
            <div style='font-size:3rem; margin-bottom:12px;'>📁</div>
            <div style='font-weight:700; color:#C0C0D8; margin-bottom:6px;'>No CVs loaded</div>
            <div style='font-size:0.88rem;'>Upload PDF resumes above</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown("<br>", unsafe_allow_html=True)
    col_h, col_btn = st.columns([3, 1])
    with col_h:
        st.markdown(f"### 📋 Loaded CVs ({len(candidates)})")
    with col_btn:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state["candidates"] = []
            st.rerun()

    # Use st.columns for proper table alignment
    # Header
    h1, h2, h3, h4, h5, h6 = st.columns([3, 1.2, 1.2, 1, 1.8, 1.5])
    with h1:
        st.markdown("<div style='color:#8888A8; font-size:0.75rem; text-transform:uppercase; font-weight:600; padding:8px 0; border-bottom:1px solid #252545;'>Candidate</div>", unsafe_allow_html=True)
    with h2:
        st.markdown("<div style='color:#8888A8; font-size:0.75rem; text-transform:uppercase; font-weight:600; padding:8px 0; border-bottom:1px solid #252545;'>Score</div>", unsafe_allow_html=True)
    with h3:
        st.markdown("<div style='color:#8888A8; font-size:0.75rem; text-transform:uppercase; font-weight:600; padding:8px 0; border-bottom:1px solid #252545;'>Skills</div>", unsafe_allow_html=True)
    with h4:
        st.markdown("<div style='color:#8888A8; font-size:0.75rem; text-transform:uppercase; font-weight:600; padding:8px 0; border-bottom:1px solid #252545;'>Exp</div>", unsafe_allow_html=True)
    with h5:
        st.markdown("<div style='color:#8888A8; font-size:0.75rem; text-transform:uppercase; font-weight:600; padding:8px 0; border-bottom:1px solid #252545;'>Decision</div>", unsafe_allow_html=True)
    with h6:
        st.markdown("<div style='color:#8888A8; font-size:0.75rem; text-transform:uppercase; font-weight:600; padding:8px 0; border-bottom:1px solid #252545;'>Status</div>", unsafe_allow_html=True)

    for i, c in enumerate(candidates):
        sc    = c.get("scores") or {}
        name  = sc.get("name") or c["filename"].replace(".pdf","")
        score = sc.get("overall_score","—")
        skill = sc.get("skills_score","—")
        exp   = sc.get("experience_years","—")
        dec   = sc.get("decision","Pending")
        analyzed = "overall_score" in sc

        s_col = "#43E97B" if isinstance(score,int) and score>=75 else (
                "#FFD700" if isinstance(score,int) and score>=55 else
                "#FF6B6B" if isinstance(score,int) else "#8888A8")
        dec_color = {"Strong Hire":"#43E97B","Hire":"#6C63FF","Maybe":"#FFD700",
                     "Weak Maybe":"#FF9944","Not Recommended":"#FF6B6B",
                     "Pending":"#8888A8"}.get(dec,"#8888A8")

        r1, r2, r3, r4, r5, r6 = st.columns([3, 1.2, 1.2, 1, 1.8, 1.5])

        with r1:
            st.markdown(f"""
            <div style='padding:10px 0; border-bottom:1px solid #1A1A30;'>
                <div style='font-weight:600; font-size:0.88rem; color:#E8E8F8;'>{name}</div>
                <div style='color:#555577; font-size:0.72rem; margin-top:2px;'>{c["filename"]}</div>
            </div>""", unsafe_allow_html=True)

        with r2:
            score_txt = f"{score}/100" if isinstance(score, int) else "—"
            st.markdown(f"""
            <div style='padding:10px 0; border-bottom:1px solid #1A1A30;'>
                <span style='font-family:monospace; font-weight:800;
                             color:{s_col}; font-size:0.95rem;'>{score_txt}</span>
            </div>""", unsafe_allow_html=True)

        with r3:
            skill_txt = f"{skill}%" if isinstance(skill, int) else "—"
            st.markdown(f"""
            <div style='padding:10px 0; border-bottom:1px solid #1A1A30;'>
                <span style='color:#43E97B; font-size:0.88rem;'>{skill_txt}</span>
            </div>""", unsafe_allow_html=True)

        with r4:
            exp_txt = f"{exp}y" if exp != "—" else "—"
            st.markdown(f"""
            <div style='padding:10px 0; border-bottom:1px solid #1A1A30;'>
                <span style='color:#9090B0; font-size:0.88rem;'>{exp_txt}</span>
            </div>""", unsafe_allow_html=True)

        with r5:
            st.markdown(f"""
            <div style='padding:10px 0; border-bottom:1px solid #1A1A30;'>
                <span style='color:{dec_color}; font-weight:700;
                             font-size:0.78rem;'>{dec}</span>
            </div>""", unsafe_allow_html=True)

        with r6:
            status_color = "#43E97B" if analyzed else "#8888A8"
            status_txt   = "✅ Analyzed" if analyzed else "⏳ Pending"
            st.markdown(f"""
            <div style='padding:10px 0; border-bottom:1px solid #1A1A30;'>
                <span style='color:{status_color}; font-size:0.78rem;'>{status_txt}</span>
            </div>""", unsafe_allow_html=True)

    # Re-analyze pending
    unanalyzed = [c for c in candidates if not c.get("scores")]
    if unanalyzed:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"🔄 Analyze {len(unanalyzed)} Pending CV(s)"):
            pb = st.progress(0)
            for i, c in enumerate(unanalyzed):
                _run_analysis(c, jd, weights, use_ai=has_api)
                pb.progress((i+1)/len(unanalyzed))
            st.rerun()
