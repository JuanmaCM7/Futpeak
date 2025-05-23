import streamlit as st
from pathlib import Path
import base64
from PIL import Image
import requests
import os
import pandas as pd

from data_loader import (
    load_future_metadata,
    get_metadata_by_player,
    get_matchlogs_by_player,
    get_player_image_path
)
from model_runner import predict_and_project_player
from player_processing import build_player_df, summarize_basic_stats
from stats import plot_player_stats, plot_rating_projection, plot_minutes_per_year  
from .descriptions import generar_conclusion_completa

from styles.theme import apply_background


# Configuración general y estilos
st.set_page_config(page_title="Futpeak", layout="wide", initial_sidebar_state="expanded")

# Cargar y aplicar CSS personalizado
def _load_custom_css():
    css_path = Path(__file__).parent / "styles" / "styles.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    # Override para eliminar bordes de st.image
    st.markdown(
        """
        <style>
            .stImage > div {
                border: none !important;
                box-shadow: none !important;
            }
            html, body, .stApp, .main, .block-container {
                overflow-y: auto !important;
            }
        </style>
        """, unsafe_allow_html=True
    )

_load_custom_css()
apply_background()


# Sidebar: logo, instrucciones y selector de jugador
with st.sidebar:
    logo_path = Path(__file__).parent / "assets" / "logo_no_bg_preview_3.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"<div class='fixed-logo-wrapper'><img class='fixed-logo' src='data:image/png;base64,{encoded}'/></div>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    

    st.markdown(
        """
        <h2 style='
            white-space: nowrap;
            margin: 0 0 0.5rem 0;
            color: #ffffff;
            font-size: 1rem;
        '>
            ℹ️ ¿Cómo funciona Futpeak?
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.info("""
        1. Selecciona un jugador del menú desplegable.  
        2. Visualiza al instante su resumen de carrera y proyección.  
        3. Compara con grupos de jugadores similares.  
    """)

    metadata = load_future_metadata()
    player_names = sorted(metadata["Player_name"].dropna().unique())

    st.markdown(
        "<p style='margin:0 0 0.4rem 0; white-space: nowrap; color:#ffffff; font-size:1rem;'>"
        "👤 Selecciona un jugador:</p>",
        unsafe_allow_html=True
    )
    selected_player = st.selectbox(
        label="👤 Selecciona un jugador:",
        options=player_names,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("""
    <style>
    div[data-baseweb="menu"] [role="option"] {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ⚠️ Aviso para usuarios en modo oscuro
    st.markdown("""
    <p style="
    font-size: 0.85rem;
    background-color: #fff3cd;
    color: #856404;
    padding: 10px;
    border-radius: 6px;
    margin-bottom: 0.5rem;
    font-weight: bold;
    ">
    ⚠️ Si el selector no se ve correctamente, cambia tu navegador o dispositivo a <strong>modo claro</strong>.
    </p>
    """, unsafe_allow_html=True)

    id_series = metadata.loc[metadata["Player_name"] == selected_player, "Player_ID"]
    player_id = id_series.iloc[0] if not id_series.empty else None

    st.markdown(
        """
        <p style="
        font-size: 0.85rem;
        color: #CCCCCC;
        margin-top: 0.2rem;
        line-height: 1.2;
        ">
        ⚙️ <em>Herramienta en desarrollo:</em> próximamente añadiremos variables como 
        traspasos, historial de lesiones y más métricas avanzadas.
        </p>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSfuuXMKtFDsAtQzLXoXuIlxOKQM3oPiEQtpyBJrfbxazAk2GQ/viewform?usp=dialog" target="_blank">
            <button style="
                background-color:#FFD700;
                color:black;
                font-weight:bold;
                padding:0.5em 1em;
                margin-top: 0.5rem;
                border:none;
                border-radius:8px;
                font-size:1rem;
                cursor:pointer;
                width:100%;
            ">
                📝 Enviar feedback
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
    <h1 style="font-size:2rem; margin-bottom:0.5rem;">🏟️ ¡Bienvenido a Futpeak!</h1>
    <p style='font-size:1.3rem; line-height:1.5;'>
      Futpeak es una herramienta de scouting que te ayuda a evaluar y proyectar el potencial  
      de jóvenes futbolistas basándose en datos de jugadores con trayectorias profesionales similares.
    </p>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([0.7, 1, 1.8], gap="medium")

with col1:
    if player_id is not None:
        img_path = get_player_image_path(selected_player, metadata)
        if img_path:
            img = Image.open(img_path)
            st.image(img, use_container_width=True)
        else:
            st.info("⚠️ Imagen no disponible para este jugador.")
    else:
        st.error("⚠️ No se encontró el ID del jugador.")

    if player_id is not None:
        meta = get_metadata_by_player(selected_player, future=True)
        raw_age = str(meta.get("Age", "N/A"))
        age_display = raw_age.split("-")[0] if "-" in raw_age else raw_age

        summary_df = summarize_basic_stats(build_player_df(player_id))

        profile_html = f"""
        <div class='block-card'>
            <h3>📋 Perfil del jugador</h3>
            <p><strong>Nombre:</strong> {selected_player}</p>
            <p><strong>Edad:</strong> {age_display}</p>
            <p><strong>Posición:</strong> {meta.get('Position', 'N/A')}</p>
            <p><strong>Minutos jugados:</strong> {int(summary_df['Minutos totales'].iloc[0])}</p>
        </div>
        """
        st.markdown(profile_html, unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 Producción Ofensiva")
    if player_id is not None:
        fig_stats = plot_player_stats(player_id)
        st.pyplot(fig_stats)
    else:
        st.warning("⚠️ Selecciona un jugador para ver sus estadísticas.")

    st.markdown("### ⏱️ Minutos por Año")
    if player_id is not None:
        fig_minutes = plot_minutes_per_year(player_id)
        fig_minutes.set_size_inches(6, 3)
        st.pyplot(fig_minutes)
    else:
        st.warning("⚠️ Selecciona un jugador para ver los minutos por año.")

with col3:
    st.markdown("### 📈 Predicción de grupo y evolución")
    if player_id is not None:
        label, seasonal, group_curve = predict_and_project_player(player_id)
        player_name = metadata.loc[metadata["Player_ID"] == player_id, "Player_name"].values[0]
        fig_proj = plot_rating_projection(player_name, seasonal, group_curve, label)
        fig_proj.set_size_inches(6, 4)
        st.pyplot(fig_proj)
    else:
        st.warning("⚠️ Selecciona un jugador para ver la proyección.")

conclusion_text = generar_conclusion_completa(player_id)
conclusion_text = conclusion_text.replace("## ", "")


st.markdown(f"""
<div class='block-card'>
  <h3>🔮 Conclusiones</h3>
  <p style="font-size:20px; line-height:1.4;">
    {conclusion_text}
  </p>
</div>
""", unsafe_allow_html=True)
