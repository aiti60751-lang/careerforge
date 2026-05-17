"""pages/job_setup.py"""
import streamlit as st
from data.skills_db import extract_skills
from utils.ui_components import section_header

SAMPLE_JD = """Job Title: Senior Data Scientist

We are looking for a Senior Data Scientist to join our AI/ML team.

Requirements:
- 5+ years of experience in machine learning or data science
- Strong Python skills (pandas, numpy, scikit-learn)
- Experience with deep learning frameworks (PyTorch or TensorFlow)
- Familiarity with NLP and large language models
- Cloud experience (AWS, GCP, or Azure)
- Experience with MLOps and model deployment (Docker, Kubernetes)
- SQL and database skills
- Strong communication skills for stakeholder presentations

Nice to have:
- PhD or MSc in Computer Science, Statistics, or related field
- Experience with Apache Spark or distributed computing
- Contributions to open source ML projects

Responsibilities:
- Design and deploy machine learning models at scale
- Lead data science projects end-to-end
- Collaborate with product and engineering teams
- Mentor junior data scientists
"""


def show():
    section_header("Job Setup", "Define the role — AI uses this to score and rank all candidates")

    tab1, tab2 = st.tabs(["📝 Job Description", "⚖️ Ranking Weights"])

    # ── Tab 1: JD ─────────────────────────────────────────────────────────────
    with tab1:
        col_main, col_side = st.columns([3, 2], gap="large")

        with col_main:
            jd = st.text_area(
                "Job Description",
                value=st.session_state.get("job_description", ""),
                height=420,
                placeholder="Paste the full job description here — include requirements, responsibilities, and required skills for best results...",
            )

            col_a, col_b, col_c = st.columns([2, 2, 1])
            with col_a:
                if st.button("💾 Save Job Description", use_container_width=True):
                    if jd.strip():
                        st.session_state["job_description"] = jd.strip()
                        # Clear previous analyses
                        for c in st.session_state.get("candidates", []):
                            c["scores"] = None
                            c["ai"] = None
                        # Clear summary cache
                        for k in list(st.session_state.keys()):
                            if k.startswith("exec_summary"):
                                del st.session_state[k]
                        st.success("✅ Saved! Previous analyses cleared.")
                    else:
                        st.warning("Please enter a job description.")
            with col_b:
                if st.button("📄 Load Sample (Data Science)", use_container_width=True):
                    st.session_state["job_description"] = SAMPLE_JD
                    st.rerun()
            with col_c:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state["job_description"] = ""
                    st.rerun()

        with col_side:
            if st.session_state.get("job_description"):
                jd_text = st.session_state["job_description"]
                jd_skills = extract_skills(jd_text)

                st.markdown("""<div style='background:#16162A; border:1px solid #252545;
                    border-radius:14px; padding:20px;'>
                    <div class='cf-label' style='margin-bottom:12px;'>Detected JD Skills</div>""",
                            unsafe_allow_html=True)

                by_cat = {}
                for s in jd_skills:
                    by_cat.setdefault(s["category"], []).append(s["skill"])

                for cat, skills in list(by_cat.items())[:6]:
                    cat_label = cat.replace("_", " ").title()
                    tags = " ".join(
                        f"<span style='display:inline-block; background:rgba(108,99,255,0.15); "
                        f"color:#A09AFF; border:1px solid rgba(108,99,255,0.3); border-radius:100px; "
                        f"padding:2px 9px; font-size:0.75rem; margin:2px;'>{s}</span>"
                        for s in skills[:5]
                    )
                    st.markdown(f"""
                    <div style='margin-bottom:12px;'>
                        <div style='color:#6060A0; font-size:0.7rem; margin-bottom:4px;'>{cat_label}</div>
                        <div>{tags}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f"""</div>
                <div style='background:#0D1F14; border:1px solid rgba(67,233,123,0.25);
                    border-radius:10px; padding:12px 16px; margin-top:12px;
                    color:#80F0A0; font-size:0.85rem;'>
                    ✅ {len(jd_skills)} skills detected in JD
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:#1F0D0D; border:1px solid rgba(255,107,107,0.25);
                    border-radius:12px; padding:20px; text-align:center;'>
                    <div style='color:#FF6B6B; font-weight:700; margin-bottom:6px;'>❌ No Job Description</div>
                    <div style='color:#8888A8; font-size:0.85rem;'>Set a job description to unlock CV analysis</div>
                </div>""", unsafe_allow_html=True)

                st.markdown("""<br>
                <div style='background:#16162A; border:1px solid #252545; border-radius:12px; padding:16px;'>
                    <div class='cf-label' style='margin-bottom:10px;'>💡 Tips for Better Results</div>
                    <div style='color:#9090B0; font-size:0.82rem; line-height:1.8;'>
                        • Include specific tools and technologies<br>
                        • Mention required years of experience<br>
                        • Separate must-have vs nice-to-have<br>
                        • Add education requirements<br>
                        • Include seniority level
                    </div>
                </div>""", unsafe_allow_html=True)

    # ── Tab 2: Weights ────────────────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div style='background:#16162A; border:1px solid #252545; border-radius:14px; padding:24px; max-width:600px;'>
            <div style='font-weight:700; margin-bottom:6px;'>Ranking Weight Configuration</div>
            <div style='color:#8888A8; font-size:0.85rem; margin-bottom:24px;'>
                Adjust how much each dimension contributes to the overall score.
                Weights should sum to 100.
            </div>
        """, unsafe_allow_html=True)

        w = st.session_state["weights"]

        w["skills"]     = st.slider("🎯 Skills Match",  0, 100, w["skills"],  5,
                                    help="How well the candidate's skills match the JD requirements")
        w["experience"] = st.slider("💼 Experience",    0, 100, w["experience"], 5,
                                    help="Years of experience vs required")
        w["education"]  = st.slider("🎓 Education",     0, 100, w["education"],  5,
                                    help="Education level (PhD > Masters > Bachelors)")
        w["ats"]        = st.slider("🤖 ATS Keywords",  0, 100, w["ats"],        5,
                                    help="Keyword density match between CV and JD")

        total = sum(w.values())
        color = "#43E97B" if total == 100 else "#FF6B6B"
        label = "✅ Perfect!" if total == 100 else f"⚠️ Total = {total} (should be 100)"

        st.markdown(f"""
        <div style='background:#252545; border-radius:8px; padding:12px 16px; margin:16px 0;
                    display:flex; justify-content:space-between; align-items:center;'>
            <span style='color:#9090B0;'>Total Weight</span>
            <span style='color:{color}; font-weight:700; font-size:1.1rem;'>{total}% — {label}</span>
        </div>""", unsafe_allow_html=True)

        if st.button("💾 Save Weights", use_container_width=False):
            st.session_state["weights"] = w
            # Reset scores so they use new weights
            for c in st.session_state.get("candidates", []):
                c["scores"] = None
                c["ai"] = None
            st.success("Weights saved! Re-run analysis to apply new weights.")

        st.markdown("""</div>
        <br>
        <div style='background:#16162A; border:1px solid #252545; border-radius:12px; padding:18px; max-width:600px;'>
            <div class='cf-label' style='margin-bottom:10px;'>Weight Presets</div>
            <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;'>
        """, unsafe_allow_html=True)

        presets = {
            "Technical Role":   {"skills":50,"experience":30,"education":10,"ats":10},
            "Management Role":  {"skills":30,"experience":40,"education":15,"ats":15},
            "Entry Level":      {"skills":35,"experience":15,"education":35,"ats":15},
        }

        for name, vals in presets.items():
            if st.button(name, use_container_width=True):
                st.session_state["weights"] = vals
                st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)
