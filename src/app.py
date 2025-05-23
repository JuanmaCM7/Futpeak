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

# Fondo
apply_background()

# Sidebar con logo y selector
with st.sidebar:
    logo_path = Path(__file__).parent / "assets" / "logo_no_bg_preview_3.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"<img src='data:image/png;base64,{encoded}' width='180'/>", unsafe_allow_html=True)

    st.subheader("ℹ️ ¿Cómo funciona Futpeak?")
    st.markdown("""
        1. Selecciona un jugador del menú desplegable.  
        2. Visualiza al instante su resumen de carrera y proyección.  
        3. Compara con grupos de jugadores similares.
    """)

    metadata = load_future_metadata()
    player_names = sorted(metadata["Player_name"].dropna().unique())

    selected_player = st.selectbox("👤 Selecciona un jugador:", player_names)

    player_id = metadata.loc[metadata["Player_name"] == selected_player, "Player_ID"].values[0]

    st.markdown("_Herramienta en desarrollo: próximamente añadiremos variables como traspasos, historial de lesiones y más métricas avanzadas._")
    st.markdown("""
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSfuuXMKtFDsAtQzLXoXuIlxOKQM3oPiEQtpyBJrfbxazAk2GQ/viewform?usp=dialog" target="_blank">
            <button>Enviar feedback</button>
        </a>
    """, unsafe_allow_html=True)

# Título principal
st.title("🏟️ ¡Bienvenido a Futpeak!")
st.write("Futpeak es una herramienta de scouting que te ayuda a evaluar y proyectar el potencial de jóvenes futbolistas basándose en datos de jugadores con trayectorias profesionales similares.")

# Columnas principales
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

# Conclusión final
conclusion_text = generar_conclusion(player_id)
st.subheader("🔮 Conclusiones")
st.markdown(conclusion_text)
