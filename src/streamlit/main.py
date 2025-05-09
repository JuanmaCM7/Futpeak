# main.py
import streamlit as st
from theme import apply_background
from pathlib import Path
import base64

st.set_page_config(page_title="Futpeak App", layout="wide", initial_sidebar_state="expanded")
apply_background()

# Load custom styles
css_path = Path(__file__).parent / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Sidebar with player input ---
with st.sidebar:
    logo_path = Path(__file__).parent / "assets" / "logo_no_bg_preview.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div style="text-align:center;margin-top:-1rem;margin-bottom:0.5rem;"><img src="data:image/png;base64,{encoded}" width="200"/></div>',
            unsafe_allow_html=True,
        )

    st.markdown("## 👤 Player Input")
    st.text_input("Player Name", "Young Prospect")
    st.slider("Age", 15, 25, 18)
    st.selectbox("Position", ["Forward", "Midfielder", "Defender", "Goalkeeper"])
    st.slider("Minutes Played", 0, 3800, 1500)
    st.selectbox("Injury History", ["None", "Minor", "Major"])
    st.button("Apply Player Data")

    st.markdown("---")
    st.markdown("### ℹ️ About Futpeak")
    st.write("Futpeak is a tool to visualize, compare and project young footballers' careers based on historical player data.")

# --- Manual navigation ---
pages = {
    "🏠 Home": "1_🏠_Home",
    "🔎 Explorer": "2_🔎_Player_Explorer",
    "📈 Evolution": "3_📈_Player_Evolution",
    "⚖️ Comparison": "4_⚖️_Comparison",
    "🔮 Projection": "5_🔮_Projection"
}

st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
for i, (label, filename) in enumerate(pages.items()):
    with [col1, col2, col3, col4, col5][i]:
        if st.button(label):
            st.experimental_set_query_params(page=filename)
            st.rerun()


# Default content if not rerouted
st.title("🏟️ Welcome to Futpeak")
st.markdown("""
Futpeak is a scouting tool that helps you evaluate and project the potential of young footballers based on data from players with similar career paths.

Use the sidebar to define a fictional or real player profile, and navigate above to explore comparisons, evolution models, and future projections.
""")

