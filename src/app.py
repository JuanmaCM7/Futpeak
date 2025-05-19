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
from stats import plot_player_stats, plot_rating_projection, plot_minutes_per_year  # nueva función
from styles.theme import apply_background

# Configuración general y estilos
st.set_page_config(page_title="Futpeak", layout="wide", initial_sidebar_state="expanded")
apply_background()

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
        </style>
        """, unsafe_allow_html=True
    )

_load_custom_css()

# Sidebar: logo e instrucciones y selector de jugador
with st.sidebar:
    logo_path = Path(__file__).parent / "assets" / "logo_no_bg_preview_3.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"<div class='fixed-logo-wrapper'><img class='fixed-logo' src='data:image/png;base64,{encoded}'/></div>",
            unsafe_allow_html=True
        )

    # Un pequeño salto
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # Luego el título
    st.markdown(
        "<h2 style='white-space: nowrap; margin-bottom: 1rem;'>ℹ️ ¿Cómo funciona Futpeak?</h2>",
        unsafe_allow_html=True
    )
    st.info("""
        1. Selecciona un jugador del menú desplegable. 
        2. Visualiza al instante su resumen de carrera y proyección.  
        3. Compara con grupos de jugadores similares.  
    """)

    metadata = load_future_metadata()
    player_names = sorted(metadata["Player_name"].dropna().unique())
    selected_player = st.selectbox("👤 Selecciona un jugador:", player_names, index=0)
    id_series = metadata.loc[metadata["Player_name"] == selected_player, "Player_ID"]
    player_id = id_series.iloc[0] if not id_series.empty else None

# Título principal
st.markdown(
    "# 🏟️ ¡Bienvenido a Futpeak!\n"
    "Futpeak es una herramienta de scouting que te ayuda a evaluar y proyectar el potencial de jóvenes futbolistas basándose en datos de jugadores con trayectorias profesionales similares."
)

# Estructura de columnas: mantenemos ratio original (0.5, 1, 1.8)
col1, col2, col3 = st.columns([0.5, 1, 1.8], gap="large")

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

    # Perfil del jugador
    if player_id is not None:
        meta = get_metadata_by_player(selected_player, future=True)
        summary_df = summarize_basic_stats(build_player_df(player_id))
        profile_html = f"""
        <div class='block-card'>
            <h3>📋 Perfil del jugador</h3>
            <p><strong>Nombre:</strong> {selected_player}</p>
            <p><strong>Edad:</strong> {meta.get('Age', 'N/A')}</p>
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

    # Nueva sección: Minutos por Año
    st.markdown("### ⏱️ Minutos por Año")
    if player_id is not None:
        fig_minutes = plot_minutes_per_year(player_id)
        # Ajuste de tamaño para que coincida con estilo ofensivo
        fig_minutes.set_size_inches(6, 3)
        st.pyplot(fig_minutes)
    else:
        st.warning("⚠️ Selecciona un jugador para ver los minutos por año.")

with col3:
    st.markdown("### 📈 Predicción de grupo y evolución")
    if player_id is not None:
        label, seasonal, group_curve = predict_and_project_player(selected_player)
        fig_proj = plot_rating_projection(selected_player, seasonal, group_curve, label)
        # Reducimos el tamaño de la figura dentro de la columna
        fig_proj.set_size_inches(6, 4)
        st.pyplot(fig_proj)
    else:
        st.warning("⚠️ Selecciona un jugador para ver la proyección.")

# Conclusión
txt = (
    "Según el análisis de trayectoria, este jugador muestra un crecimiento sostenido "
    "en los primeros años con potencial de mantenerse por encima de la media de su grupo."
)
st.markdown(
    f"<div class='block-card'><h3>🔮 Conclusiones</h3><p>{txt}</p></div>",
    unsafe_allow_html=True
)
