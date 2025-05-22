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

# Configuración general
st.set_page_config(page_title="Futpeak", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

# CSS incrustado directamente para fuentes, colores y estilos esenciales
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Inter:wght@400;600&display=swap');

/* Oculta la barra superior */
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
    color: black !important;
    border: 1px solid #ccc !important;
    border-radius: 6px !important;
    box-shadow: none !important;
}

div[data-baseweb="select"] input {
    background-color: white !important;
    color: black !important;
}

div[data-baseweb="select"] * {
    color: black !important;
}

div[data-baseweb="select"]:hover,
div[data-baseweb="select"]:focus {
    background-color: white !important;
    color: black !important;
    border-color: #ccc !important;
}

div[data-baseweb="menu"] div[role="option"] {
    background-color: white !important;
    color: black !important;
}
div[data-baseweb="menu"] div[role="option"][aria-selected="true"] span {
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


apply_background()

# Sidebar: logo, instrucciones y selector de jugador
with st.sidebar:
    logo_path = Path(__file__).parent / "assets" / "logo_no_bg_preview_3.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div class='sidebar-logo-container' style="
                margin-bottom: 1rem;
                display: flex;
                justify-content: center;
                align-items: center;
            ">
                <img src='data:image/png;base64,{encoded}' style='width:220px; height:auto;'/>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <h2 style='font-size:1rem;'>ℹ️ ¿Cómo funciona Futpeak?</h2>
    """, unsafe_allow_html=True)

    st.info("""
        1. Selecciona un jugador del menú desplegable.  
        2. Visualiza al instante su resumen de carrera y proyección.  
        3. Compara con grupos de jugadores similares.  
    """)

    metadata = load_future_metadata()
    player_names = sorted(metadata["Player_name"].dropna().unique())

    st.markdown("<p style='margin:0 0 0.4rem 0;'>👤 Selecciona un jugador:</p>", unsafe_allow_html=True)
    selected_player = st.selectbox("👤 Selecciona un jugador:", options=player_names, index=0, label_visibility="collapsed")

    id_series = metadata.loc[metadata["Player_name"] == selected_player, "Player_ID"]
    player_id = id_series.iloc[0] if not id_series.empty else None

    st.markdown("""
    <p style="font-size: 0.85rem; color: #CCCCCC; margin-top: 0.2rem; line-height: 1.2;">
    ⚙️ <em>Herramienta en desarrollo:</em> próximamente añadiremos variables como traspasos, historial de lesiones y más métricas avanzadas.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSfuuXMKtFDsAtQzLXoXuIlxOKQM3oPiEQtpyBJrfbxazAk2GQ/viewform?usp=dialog" target="_blank">
        <button style="background-color:#FFD700; color:black; font-weight:bold; padding:0.5em 1em; margin-top: 0.5rem; border:none; border-radius:8px; font-size:1rem; cursor:pointer; width:100%;">
            📝 Enviar feedback
        </button>
    </a>
    """, unsafe_allow_html=True)

st.markdown("""
<h1 style="font-size:2rem; margin-bottom:0.5rem;">🏟️ ¡Bienvenido a Futpeak!</h1>
<p style='font-size:1.3rem; line-height:1.5;'>
  Futpeak es una herramienta de scouting que te ayuda a evaluar y proyectar el potencial  
  de jóvenes futbolistas basándose en datos de jugadores con trayectorias profesionales similares.
</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.5, 0.7, 1], gap="medium")

with col1:
    if player_id is not None:
        img_path = get_player_image_path(selected_player, metadata)
        if img_path:
            img = Image.open(img_path)
            st.image(img, use_container_width=True)
        else:
            st.info("⚠️ Imagen no disponible para este jugador.")

        meta = get_metadata_by_player(selected_player, future=True)
        raw_age = str(meta.get("Age", "N/A"))
        age_display = raw_age.split("-")[0] if "-" in raw_age else raw_age

        summary_df = summarize_basic_stats(build_player_df(player_id))

        st.markdown(f"""
        <div style='background-color: rgba(0,0,0,0.6); padding: 1rem; border-radius: 12px;'>
            <h3>📋 Perfil del jugador</h3>
            <p><strong>Nombre:</strong> {selected_player}</p>
            <p><strong>Edad:</strong> {age_display}</p>
            <p><strong>Posición:</strong> {meta.get('Position', 'N/A')}</p>
            <p><strong>Minutos jugados:</strong> {int(summary_df['Minutos totales'].iloc[0])}</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 Producción Ofensiva")
    if player_id is not None:
        fig_stats = plot_player_stats(player_id)
        st.pyplot(fig_stats)

    st.markdown("### ⏱️ Minutos por Año")
    if player_id is not None:
        fig_minutes = plot_minutes_per_year(player_id)
        fig_minutes.set_size_inches(6, 3)
        st.pyplot(fig_minutes)

with col3:
    st.markdown("### 📈 Predicción de grupo y evolución")
    if player_id is not None:
        label, seasonal, group_curve = predict_and_project_player(player_id)
        player_name = metadata.loc[metadata["Player_ID"] == player_id, "Player_name"].values[0]
        fig_proj = plot_rating_projection(player_name, seasonal, group_curve, label)
        fig_proj.set_size_inches(6, 4)
        st.pyplot(fig_proj)

conclusion_text = generar_conclusion(player_id)

st.markdown(f"""
<div style='background-color: rgba(0,0,0,0.6); padding: 1.5rem; border-radius: 12px;'>
  <h3>🔮 Conclusiones</h3>
  <p style="font-size:20px; line-height:1.4;">{conclusion_text}</p>
</div>
""", unsafe_allow_html=True)
