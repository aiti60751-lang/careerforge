import os

def get_groq_key() -> str:
    key = os.environ.get('GROQ_API_KEY', '')
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get('GROQ_API_KEY', '')
    except Exception:
        return ''
