import os
import streamlit as st

def get_groq_key() -> str:
    key = os.environ.get('GROQ_API_KEY', '')
    if key:
        return key
    try:
        return st.secrets.get('GROQ_API_KEY', '')
    except Exception:
        return ''
