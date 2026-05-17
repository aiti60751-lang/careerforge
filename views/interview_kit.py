"""views/interview_kit.py — AI-generated interview kit per candidate."""
import streamlit as st
from utils.state import get_ranked
from utils.ui_components import section_header, empty_state

DIFF_COLORS = {"Easy": "#43E97B", "Medium": "#FFD700", "Hard": "#FF6B6B"}


def get_name(c):
    return (c.get("scores") or {}).get("name") or c["filename"].replace(".pdf", "")


def show():
    section_header("Interview Kit", "AI-generated questions tailored to each candidate")

    ranked = get_ranked()
    if not ranked:
        empty_state("❓", "No Candidates", "Analyze CVs first.")
        return

    # ── Selector ──────────────────────────────────────────────────────────────
    names     = [get_name(c) for c in ranked]
    filenames = [c["filename"] for c in ranked]
    presel    = st.session_state.get("selected_filename", "")
    default   = filenames.index(presel) if presel in filenames else 0

    idx = st.selectbox(
        "Select Candidate",
        range(len(names)),
        format_func=lambda i: f"{names[i]} — {ranked[i]['scores'].get('overall_score','?')}/100",
        index=default,
    )

    c    = ranked[idx]
    sc   = c["scores"]
    ai   = c.get("ai") or {}
    jd   = st.session_state.get("job_description", "")
    name = get_name(c)

    # ── Banner ────────────────────────────────────────────────────────────────
    dec       = sc.get("decision", "Pending")
    dec_color = {"Strong Hire":"#43E97B","Hire":"#6C63FF","Maybe":"#FFD700",
                 "Weak Maybe":"#FF9944","Not Recommended":"#FF6B6B"}.get(dec,"#8888A8")

    st.markdown(f"""
    <div style='background:#16162A; border:1px solid #252545; border-radius:10px;
                padding:14px 18px; margin:12px 0;'>
        <div style='display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;'>
            <div>
                <span style='font-weight:700; color:#E8E8F8;'>{name}</span>
                <span style='color:#8888A8; margin-left:10px; font-size:0.82rem;'>
                    {ai.get("current_title","") or c["filename"]}
                </span>
            </div>
            <div style='display:flex; gap:16px; font-size:0.83rem;'>
                <span>Score: <b style='color:#A09AFF;'>{sc.get("overall_score","?")}/100</b></span>
                <span>Decision: <b style='color:{dec_color};'>{dec}</b></span>
                <span>Exp: <b style='color:#C0C0D8;'>{sc.get("experience_years","?")} yrs</b></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── API Key check ─────────────────────────────────────────────────────────
    from utils.config import get_groq_key
    api_key = get_groq_key()

    if not api_key:
        st.markdown("""
        <div style='background:#1F0D0D; border:1px solid rgba(255,107,107,0.3);
                    border-radius:12px; padding:20px; margin:16px 0;'>
            <div style='color:#FF6B6B; font-weight:700; margin-bottom:8px;'>⚠️ GROQ_API_KEY not found</div>
            <div style='color:#C0C0D0; font-size:0.88rem; line-height:1.7;'>
                Open <b>utils/config.py</b> and add this line at the top:<br>
                <code style='background:#0E0E1A; padding:4px 8px; border-radius:4px; color:#A09AFF; display:block; margin:8px 0;'>
                os.environ["GROQ_API_KEY"] = "gsk_your_key_here"
                </code>
                Then restart: <code style='background:#0E0E1A; padding:4px 8px; border-radius:4px; color:#A09AFF;'>streamlit run app.py</code>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Cache key per candidate file ─────────────────────────────────────────
    cache_key = f"iq_{c['filename']}"
    iq = st.session_state.get(cache_key)

    # ── Buttons ───────────────────────────────────────────────────────────────
    col_gen, col_regen, _ = st.columns([1, 1, 3])

    with col_gen:
        if not iq:
            generate = st.button("🚀 Generate Interview Kit", use_container_width=True)
        else:
            generate = False

    with col_regen:
        if iq:
            if st.button("🔄 Regenerate", use_container_width=True):
                del st.session_state[cache_key]
                st.rerun()

    # ── Run generation OUTSIDE column context ─────────────────────────────────
    if generate:
        with st.spinner(f"Building interview kit for {name}..."):
            try:
                from utils.ai_engine import generate_interview_kit
                merged = {**sc, **ai}
                result = generate_interview_kit(c["text"], jd, merged)
                st.session_state[cache_key] = result
                st.session_state["current_page"] = "❓ Interview Kit"
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        return

    # ── Not generated yet ─────────────────────────────────────────────────────
    if not iq:
        st.markdown("""
        <div style='background:#16162A; border:1px solid #252545; border-radius:12px;
                    padding:24px; margin-top:16px;'>
            <div class='cf-label' style='margin-bottom:12px;'>What you'll get</div>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:10px;
                        font-size:0.85rem; color:#9090B0;'>
                <div>🔧 5 Technical questions (Easy → Hard)</div>
                <div>💬 4 Behavioral questions with STAR guidance</div>
                <div>📐 3 Situational scenarios</div>
                <div>🚩 Targeted red-flag probes</div>
                <div>👋 2 Opening questions</div>
                <div>🎤 Custom closing question</div>
            </div>
        </div>""", unsafe_allow_html=True)
        return

    if isinstance(iq, dict) and "error" in iq:
        st.error(f"Failed: {iq['error']}")
        return

    # ── Display Tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👋 Opening", "🔧 Technical", "💬 Behavioral", "📐 Situational", "🚩 Red Flags"
    ])

    with tab1:
        for q in iq.get("opening_questions", []):
            st.markdown(f"""
            <div style='background:#16162A; border:1px solid #252545; border-radius:12px;
                        padding:20px; margin:10px 0;'>
                <div style='font-weight:700; color:#E8E8F8; margin-bottom:8px;'>💬 {q.get("q","")}</div>
                <div style='color:#8888A8; font-size:0.72rem; text-transform:uppercase; margin-bottom:4px;'>Purpose</div>
                <div style='color:#A0A0C0; font-size:0.85rem;'>{q.get("purpose","")}</div>
            </div>""", unsafe_allow_html=True)
        closing = iq.get("closing","")
        if closing:
            st.markdown(f"""
            <div style='background:rgba(108,99,255,0.08); border:1px solid rgba(108,99,255,0.25);
                        border-radius:12px; padding:18px; margin-top:16px;'>
                <div class='cf-label' style='margin-bottom:8px;'>🎤 Recommended Closing</div>
                <div style='font-weight:700; color:#C0BCFF;'>{closing}</div>
            </div>""", unsafe_allow_html=True)

    with tab2:
        for q in iq.get("technical", []):
            diff  = q.get("difficulty","Medium")
            d_col = DIFF_COLORS.get(diff,"#8888A8")
            skill = q.get("skill_tested","")
            st.markdown(f"""
            <div style='background:#16162A; border:1px solid #252545; border-radius:12px;
                        padding:20px; margin:10px 0;'>
                <div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;'>
                    <div style='font-weight:700; color:#E8E8F8; flex:1; margin-right:12px;'>🔧 {q.get("q","")}</div>
                    <div style='display:flex; gap:6px; flex-shrink:0;'>
                        {f"<span style='background:rgba(108,99,255,0.15); color:#A09AFF; border:1px solid rgba(108,99,255,0.3); border-radius:100px; padding:2px 10px; font-size:0.72rem;'>{skill}</span>" if skill else ""}
                        <span style='color:{d_col}; border:1px solid {d_col}40; border-radius:100px; padding:2px 10px; font-size:0.72rem; font-weight:700;'>{diff}</span>
                    </div>
                </div>
                <div style='background:#0E0E1A; border-radius:8px; padding:14px;'>
                    <div style='color:#6060A0; font-size:0.7rem; text-transform:uppercase; margin-bottom:6px;'>Ideal Answer</div>
                    <div style='color:#B0B0D0; font-size:0.85rem; line-height:1.6;'>{q.get("ideal","")}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("""<div style='background:rgba(108,99,255,0.06); border:1px solid rgba(108,99,255,0.15);
            border-radius:10px; padding:12px 16px; margin-bottom:14px; font-size:0.83rem; color:#9090C0;'>
            💡 Use <b>STAR method</b>: Situation → Task → Action → Result
        </div>""", unsafe_allow_html=True)
        for q in iq.get("behavioral", []):
            comp = q.get("competency","")
            st.markdown(f"""
            <div style='background:#16162A; border:1px solid #252545; border-radius:12px;
                        padding:20px; margin:10px 0;'>
                {f"<div style='color:#6C63FF; font-size:0.7rem; font-weight:700; text-transform:uppercase; margin-bottom:8px;'>COMPETENCY: {comp}</div>" if comp else ""}
                <div style='font-weight:700; color:#E8E8F8; margin-bottom:10px;'>💬 {q.get("q","")}</div>
                <div style='color:#8888A8; font-size:0.72rem; text-transform:uppercase; margin-bottom:4px;'>What to Look For</div>
                <div style='color:#A0A0C0; font-size:0.85rem; line-height:1.5;'>{q.get("look_for","")}</div>
            </div>""", unsafe_allow_html=True)

    with tab4:
        for q in iq.get("situational", []):
            st.markdown(f"""
            <div style='background:#16162A; border:1px solid #252545; border-radius:12px;
                        padding:20px; margin:10px 0;'>
                <div style='font-weight:700; color:#E8E8F8; margin-bottom:10px;'>📐 {q.get("q","")}</div>
                <div style='background:#0E0E1A; border-radius:8px; padding:14px;'>
                    <div style='color:#6060A0; font-size:0.7rem; text-transform:uppercase; margin-bottom:6px;'>Strong Response Includes</div>
                    <div style='color:#B0B0D0; font-size:0.85rem; line-height:1.6;'>{q.get("ideal","")}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab5:
        probes = iq.get("red_flag_probes", [])
        if not probes:
            st.markdown("<p style='color:#8888A8;'>✅ No specific red flags for this candidate.</p>",
                        unsafe_allow_html=True)
        else:
            for p in probes:
                st.markdown(f"""
                <div style='background:#16162A; border:1px solid rgba(255,107,107,0.25);
                            border-left:3px solid #FF6B6B; border-radius:0 10px 10px 0;
                            padding:18px; margin:10px 0;'>
                    <div style='color:#FF9E9E; font-size:0.75rem; font-weight:700;
                                text-transform:uppercase; margin-bottom:8px;'>
                        🚩 Concern: {p.get("concern","")}
                    </div>
                    <div style='font-weight:700; color:#E8E8F8;'>{p.get("q","")}</div>
                </div>""", unsafe_allow_html=True)
