# app.py
import streamlit as st
from pathlib import Path
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

from data_loader import (
    load_future_metadata,
    get_metadata_by_player,
    get_matchlogs_by_player,
    get_player_image_path,
    get_name_id_mapping
)
from model_runner import predict_and_project_player
from player_processing import build_player_df, calculate_rating_per_90, summarize_basic_stats
from stats import plot_player_stats, plot_rating_projection
from styles.theme import apply_background

# Configuración general y estilos
st.set_page_config(page_title="Futpeak", layout="wide", initial_sidebar_state="expanded")
apply_background()

# Estilos CSS personalizados
css_path = Path(__file__).parent / "styles" / "styles.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar con logo e instrucciones
with st.sidebar:
    logo_path = Path(__file__).parent / "assets" / "logo_no_bg_preview_3.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded_logo = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
                .fixed-logo-wrapper {{ width: 100%; margin-bottom: -1rem; }}
                .fixed-logo {{ width: 240px; height: auto; }}
            </style>
            <div class="fixed-logo-wrapper">
                <img class="fixed-logo" src="data:image/png;base64,{encoded_logo}" alt="Futpeak Logo">
            </div>
        """, unsafe_allow_html=True)

    st.markdown("------")
    st.markdown("### ℹ️ How to use Futpeak")
    st.info("""
        1. Select a player from the dropdown.
        2. Instantly view their career summary and projection.
        3. Compare against similar player groups.
    """)

    st.markdown("## 👤 Player Selector")
    metadata = load_future_metadata()
    player_names = sorted(metadata["Player_name"].dropna().unique())
    selected_player = st.selectbox("Choose a player", player_names, index=0)
    player_id = metadata[metadata['Player_name'] == selected_player]['Player_ID'].values[0]

# Título principal
st.markdown("""
    <div style='margin-top: -40px;'>
        <h1 style='font-size: 2.5rem;'>🏟️ Welcome to Futpeak</h1>
        <p style='font-size: 1.1rem;'>Futpeak is a scouting tool that helps you evaluate and project the potential of young footballers based on data from players with similar career paths.</p>
    </div>
""", unsafe_allow_html=True)

# Columnas principales
col1, col2, col3 = st.columns([0.5, 1, 1.8], gap="large")

with col1:
    st.markdown("### 🖼️ Player Image")
    img_path = get_player_image_path(selected_player)
    if img_path and img_path.exists():
        img = Image.open(img_path)
        st.image(img, use_column_width=True)
    else:
        st.info("⚠️ Imagen no disponible para este jugador.")

    if selected_player:
        meta = get_metadata_by_player(selected_player, future=True)
        summary_df = summarize_basic_stats(build_player_df(player_id))
        profile_html = f"""
        <div class="block-card" style="margin-top: 20px; padding: 1rem 1rem;">
            <h3>📋 Player Profile</h3>
            <p><strong>Nombre:</strong> {selected_player}</p>
            <p><strong>Edad:</strong> {meta.get('Age', 'N/A')}</p>
            <p><strong>Posición:</strong> {meta.get('Position', 'N/A')}</p>
            <p><strong>Minutos jugados:</strong> {int(summary_df['Minutos totales'].values[0])}</p>
        </div>
        """
        st.markdown(profile_html, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style='margin-top: 1.5rem;'>
            <h4>📊 Producción Ofensiva</h4>
        </div>
    """, unsafe_allow_html=True)
    fig_stats = plot_player_stats(player_id)
    if fig_stats is not None:
        st.pyplot(fig_stats)
    else:
        st.warning("⚠️ No se pudo generar la gráfica de estadísticas para este jugador.")

with col3:
    st.markdown("""
        <div class="block-card" style="max-width: 80%; margin-top: -0.5rem; padding: 1.2rem;">
            <h3 style="margin-bottom: 1rem;">📈 Rating Evolution</h3>
    """, unsafe_allow_html=True)

    predicted_label, player_seasonal, group_curve = predict_and_project_player(selected_player)
    fig_projection = plot_rating_projection(selected_player, player_seasonal, group_curve, predicted_label)
    st.pyplot(fig_projection)

    st.markdown("</div>", unsafe_allow_html=True)

# Conclusión textual
with st.container():
    st.markdown("""
    <div class="block-card">
        <h3>🔮 Career Projection Insight</h3>
        <p>Según el análisis de trayectoria, este jugador muestra un crecimiento sostenido en los primeros años con potencial de mantenerse por encima de la media de su grupo. Ajustado a minutos jugados y edad, su evolución es positiva.</p>
    </div>
    """, unsafe_allow_html=True)