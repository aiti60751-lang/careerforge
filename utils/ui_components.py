"""utils/ui_components.py — Reusable UI building blocks."""
import streamlit as st

DECISION_COLORS = {
    "Strong Hire":     ("#43E97B", "rgba(67,233,123,0.12)", "rgba(67,233,123,0.3)"),
    "Hire":            ("#6C63FF", "rgba(108,99,255,0.12)", "rgba(108,99,255,0.3)"),
    "Maybe":           ("#FFD700", "rgba(255,215,0,0.12)",  "rgba(255,215,0,0.3)"),
    "Weak Maybe":      ("#FF9944", "rgba(255,153,68,0.12)", "rgba(255,153,68,0.3)"),
    "Not Recommended": ("#FF6B6B", "rgba(255,107,107,0.12)","rgba(255,107,107,0.3)"),
}

DECISION_ICONS = {
    "Strong Hire": "🟢", "Hire": "🔵",
    "Maybe": "🟡", "Weak Maybe": "🟠", "Not Recommended": "🔴"
}


def score_color(score: int) -> str:
    if score >= 75: return "#43E97B"
    if score >= 60: return "#6C63FF"
    if score >= 45: return "#FFD700"
    return "#FF6B6B"


def score_badge(score: int, size: str = "normal") -> str:
    c = score_color(score)
    fs = "1.5rem" if size == "large" else "0.95rem"
    return (f"<span style='font-family:Plus Jakarta Sans,sans-serif; font-weight:800; "
            f"font-size:{fs}; color:{c};'>{score}<span style='color:#8888A8; "
            f"font-size:0.7em;'>/100</span></span>")


def decision_badge(decision: str) -> str:
    color, bg, border = DECISION_COLORS.get(decision, ("#8888A8","rgba(136,136,168,0.1)","rgba(136,136,168,0.3)"))
    icon = DECISION_ICONS.get(decision, "⚪")
    return (f"<span style='display:inline-flex; align-items:center; gap:5px; "
            f"background:{bg}; border:1px solid {border}; border-radius:100px; "
            f"padding:4px 12px; font-size:0.82rem; font-weight:600; color:{color};'>"
            f"{icon} {decision}</span>")


def mini_bar(label: str, value: int, col=None):
    """Compact score bar."""
    c = score_color(value)
    html = f"""
    <div style='margin:5px 0;'>
        <div style='display:flex; justify-content:space-between; font-size:0.78rem; margin-bottom:3px;'>
            <span style='color:#9090B0;'>{label}</span>
            <span style='color:{c}; font-weight:700;'>{value}</span>
        </div>
        <div style='background:#252535; border-radius:100px; height:5px;'>
            <div style='background:{c}; width:{value}%; height:5px; border-radius:100px; transition:width 0.5s;'></div>
        </div>
    </div>"""
    if col:
        with col: st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def skill_tag(skill: str, variant: str = "matched") -> str:
    styles = {
        "matched": "background:rgba(108,99,255,0.15);color:#A09AFF;border:1px solid rgba(108,99,255,0.3);",
        "missing": "background:rgba(255,107,107,0.1);color:#FF9E9E;border:1px solid rgba(255,107,107,0.25);",
        "extra":   "background:rgba(67,233,123,0.1);color:#80F0A0;border:1px solid rgba(67,233,123,0.25);",
    }
    s = styles.get(variant, styles["matched"])
    return (f"<span style='{s} display:inline-block; border-radius:100px; "
            f"padding:2px 10px; font-size:0.78rem; margin:2px;'>{skill}</span>")


def kpi_card(value, label: str, color: str = "#6C63FF", sub: str = ""):
    return f"""
    <div style='background:#16162A; border:1px solid #252545; border-radius:14px; padding:22px 18px;
                text-align:center; transition:border-color 0.2s;'>
        <div style='font-family:Plus Jakarta Sans,sans-serif; font-size:2.2rem; font-weight:800; color:{color};'>{value}</div>
        <div style='color:#8888A8; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; margin-top:3px;'>{label}</div>
        {f"<div style='color:#6060A0; font-size:0.7rem; margin-top:4px;'>{sub}</div>" if sub else ""}
    </div>"""


def section_header(title: str, sub: str = ""):
    st.markdown(f"""
    <div style='margin-bottom:20px;'>
        <h2 style='font-family:Plus Jakarta Sans,sans-serif; font-size:1.5rem;
                   font-weight:800; margin:0; color:#E8E8F8;'>{title}</h2>
        {f"<p style='color:#8888A8; margin:4px 0 0 0; font-size:0.9rem;'>{sub}</p>" if sub else ""}
    </div>
    """, unsafe_allow_html=True)


def empty_state(icon: str, title: str, description: str):
    st.markdown(f"""
    <div style='text-align:center; padding:60px 20px; color:#8888A8;'>
        <div style='font-size:3rem; margin-bottom:12px;'>{icon}</div>
        <h3 style='font-family:Plus Jakarta Sans,sans-serif; color:#C0C0D8; margin-bottom:8px;'>{title}</h3>
        <p style='max-width:400px; margin:0 auto; line-height:1.6;'>{description}</p>
    </div>
    """, unsafe_allow_html=True)


def risk_flag_pill(flag: str) -> str:
    return (f"<div style='background:rgba(255,107,107,0.08); border:1px solid rgba(255,107,107,0.2); "
            f"border-radius:8px; padding:8px 14px; margin:6px 0; color:#FF9E9E; font-size:0.85rem;'>"
            f"🚩 {flag}</div>")
