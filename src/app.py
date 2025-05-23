import streamlit as st
from pathlib import Path
import base64
from PIL import Image

from data_loader import (
    load_future_metadata,
    get_metadata_by_player,
    get_matchlogs_by_player,
    get_player_image_path
)
from model_runner import predict_and_project_player
from player_processing import build_player_df, summarize_basic_stats
from stats import plot_player_stats, plot_rating_projection, plot_minutes_per_year
from descriptions import generar_conclusion
from styles.theme import apply_background

# Configuración básica de la app
st.set_page_config(page_title="Futpeak", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

# CSS incrustado
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Inter:wght@400;600&display=swap');

header[data-testid="stHeader"] {
    display: none !important;
}

html {
    font-size: 90% !important;
}

html, body, .stApp {
    font-family: 'Inter', sans-serif !important;
    color: #ffffff;
    background-color: transparent;
    margin: 0 !important;
    padding: 0 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 100vw !important;
    margin: 0 auto !important;
}

section.main > div {
    max-width: 100vw !important;
    padding-top: 0 !important;
}

h1, h2, h3, h4,
.block-card h3,
[data-testid="stSidebar"] h2 {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    color: #FFD700 !important;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
}

p, span, li, ul, ol, td, th {
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    color: #ffffff;
}

.block-card {
    background-color: rgba(10, 10, 10, 0.75);
    padding: 1.5rem;
    border-radius: 16px;
    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.4);
    margin-bottom: 1.5rem;
}
.block-card p, .block-card span {
    color: #ffffff !important;
}

[data-testid="stSidebar"] {
    background-color: rgba(10, 30, 63, 0.7) !important;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    z-index: 10;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1rem 1.5rem 2rem 1.5rem !important;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    gap: 1.5rem;
    z-index: 10;
}

.sidebar-logo-container {
    margin-top: -0.5rem;
    margin-bottom: 0.2rem;
    display: flex;
    justify-content: flex-start;
    align-items: center;
}

.sidebar-logo-container img {
    width: 180px;
    height: auto;
}

[data-testid="stSidebarNav"] {
    display: none !important;
}

div[data-baseweb="select"] {
    background-color: white !important;
    border-radius: 6px !important;
    z-index: 9999 !important;
    position: relative !important;
}

div[data-baseweb="select"] * {
    color: black !important;
    z-index: 9999 !important;
    position: relative !important;
}

div[data-baseweb="menu"] div[role="option"] {
    color: black !important;
    background-color: white !important;
}

div[data-baseweb="menu"] div[role="option"][aria-selected="true"] span {
    color: black !important;
    font-weight: 700 !important;
}

.stImage > div {
    border: none !important;
    box-shadow: none !important;
}

img {
    border-radius: 50%;
    border: 3px solid #948e8e;
}

html, body, .stApp, p, span, div, li, td, th, h1, h2, h3, h4, h5, h6 {
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}
</style>
""", unsafe_allow_html=True)

# Fondo
apply_background()

# App
metadata = load_future_metadata()
player_names = sorted(metadata["Player_name"].dropna().unique())

with st.sidebar:
    logo_path = Path(__file__).parent / "assets" / "logo_no_bg_preview_3.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"<img src='data:image/png;base64,{encoded}' class='sidebar-logo-container' />", unsafe_allow_html=True)

    st.subheader("ℹ️ ¿Cómo funciona Futpeak?")
    st.markdown("""
        1. Selecciona un jugador del menú desplegable.  
        2. Visualiza al instante su resumen de carrera y proyección.  
        3. Compara con grupos de jugadores similares.
    """)

    selected_player = st.selectbox("🕤 Selecciona un jugador:", player_names)

    st.markdown("""
    <p style="font-size: 0.85rem; color: #ffecb3; background-color: #5c4f00; padding: 8px; border-radius: 6px; margin-top: 6px;">
    ⚠️ Si el selector no se ve correctamente, cambia tu navegador o dispositivo a <strong>modo claro</strong>.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("_Herramienta en desarrollo: próximamente añadiremos variables como traspasos, historial de lesiones y más métricas avanzadas._")
    st.markdown("""
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSfuuXMKtFDsAtQzLXoXuIlxOKQM3oPiEQtpyBJrfbxazAk2GQ/viewform?usp=dialog" target="_blank">
            <button>Enviar feedback</button>
        </a>
    """, unsafe_allow_html=True)

player_id = metadata.loc[metadata["Player_name"] == selected_player, "Player_ID"].values[0]

st.title("🏟️ ¡Bienvenido a Futpeak!")
st.write("Futpeak es una herramienta de scouting que te ayuda a evaluar y proyectar el potencial de jóvenes futbolistas basándose en datos de jugadores con trayectorias profesionales similares.")

col1, col2, col3 = st.columns([0.6, 0.7, 1])

with col1:
    img_path = get_player_image_path(selected_player, metadata)
    if img_path:
        st.image(img_path, use_container_width=True)

    meta = get_metadata_by_player(selected_player, future=True)
    raw_age = str(meta.get("Age", "N/A"))
    age_display = raw_age.split("-")[0] if "-" in raw_age else raw_age

    summary_df = summarize_basic_stats(build_player_df(player_id))

    st.subheader("📋 Perfil del jugador")
    st.write(f"**Nombre:** {selected_player}")
    st.write(f"**Edad:** {age_display}")
    st.write(f"**Posición:** {meta.get('Position', 'N/A')}")
    st.write(f"**Minutos jugados:** {int(summary_df['Minutos totales'].iloc[0])}")

with col2:
    st.subheader("📊 Producción Ofensiva")
    fig_stats = plot_player_stats(player_id)
    st.pyplot(fig_stats)

    st.subheader("⏱️ Minutos por Año")
    fig_minutes = plot_minutes_per_year(player_id)
    st.pyplot(fig_minutes)

with col3:
    st.subheader("📈 Predicción de grupo y evolución")
    label, seasonal, group_curve = predict_and_project_player(player_id)
    fig_proj = plot_rating_projection(selected_player, seasonal, group_curve, label)
    st.pyplot(fig_proj)

conclusion_text = generar_conclusion(player_id)
st.subheader("🔮 Conclusiones")
st.markdown(conclusion_text)
