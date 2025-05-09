import streamlit as st
from theme import apply_background
from pathlib import Path
import base64

st.set_page_config(page_title="Futpeak | Comparison", layout="wide", initial_sidebar_state="expanded")
apply_background()

css_path = Path(__file__).parent.parent / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    logo_path = Path(__file__).parent.parent / "assets" / "logo_no_bg_preview.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""<div style="text-align: center; margin-top: -0.5rem; margin-bottom: 0.5rem;">
            <img src="data:image/png;base64,{encoded}" alt="Futpeak Logo" width="220">
        </div>""", unsafe_allow_html=True)

st.markdown("""
    <div style='display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem;'>
        <a href="/?page=🏠 Home"><button class="nav-button">🏠 Home</button></a>
        <a href="/?page=🔎 Player Explorer"><button class="nav-button">🔎 Explorer</button></a>
        <a href="/?page=📈 Player Evolution"><button class="nav-button">📈 Evolution</button></a>
        <a href="/?page=⚖️ Comparison"><button class="nav-button">⚖️ Comparison</button></a>
        <a href="/?page=🔮 Projection"><button class="nav-button">🔮 Projection</button></a>
    </div>
""", unsafe_allow_html=True)

st.title("⚖️ Player Comparison")
st.write("Compare similar players side-by-side by key performance metrics.")
