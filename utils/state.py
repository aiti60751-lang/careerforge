"""utils/state.py — Centralized session state management."""
import streamlit as st


def init_state():
    """Initialize all session state variables."""
    defaults = {
        "candidates":       [],      # List of candidate dicts
        "job_description":  "",
        "job_title":        "",
        "job_id":           None,
        "weights": {
            "skills":     40,
            "experience": 30,
            "education":  15,
            "ats":        15,
        },
        "filter_decisions": ["Strong Hire", "Hire", "Maybe", "Weak Maybe", "Not Recommended"],
        "filter_min_score": 0,
        "sort_by":          "overall_score",
        "selected_idx":       0,
        "selected_filename":  "",
        "current_page":       "",
        "last_page":          "",
        "comparison_ids":     [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_analyzed() -> list[dict]:
    return [c for c in st.session_state.get("candidates", []) if c.get("scores")]


def get_ranked() -> list[dict]:
    analyzed = get_analyzed()
    return sorted(analyzed, key=lambda c: c.get("scores", {}).get("overall_score", 0), reverse=True)


def upsert_candidate(filename: str, text: str) -> dict:
    """Add candidate or return existing one."""
    for c in st.session_state["candidates"]:
        if c["filename"] == filename:
            return c
    candidate = {
        "filename": filename,
        "text":     text,
        "scores":   None,
        "ai":       None,
        "iq":       None,
        "report":   None,
    }
    st.session_state["candidates"].append(candidate)
    return candidate


def remove_candidate(idx: int):
    st.session_state["candidates"].pop(idx)


def clear_all():
    st.session_state["candidates"] = []
