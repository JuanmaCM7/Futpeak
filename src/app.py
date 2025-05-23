import streamlit as st
from pathlib import Path
import base64
from PIL import Image
import pandas as pd
import time
import os

from data_loader import (
    load_future_metadata,
    get_metadata_by_player,
    get_player_image_path
)
from model_runner import predict_and_project_player
from player_processing import build_player_df, summarize_basic_stats
from stats import (
    plot_player_stats,
    plot_minutes_per_year,
    plot_rating_projection
)
from descriptions import generar_conclusion_completa
from styles.theme import apply_background

# ---------------------------
# ✅ CONFIGURACIÓN INICIAL
# ---------------------------
st.set_page_config(page_title="Futpeak", layout="wide", initial_sidebar_state="expanded")

css_path = Path(__file__).parent / "styles" / "styles.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
    <style>
        .stImage > div {
            border: none !important;
            box-shadow: none !important;
        }
        html, body, .stApp, .main, .block-container {
            overflow-y: auto !important;
        }
        [data-testid="stSidebar"] {
            padding-top: -2.0rem !important;
        }
    </style>
""", unsafe_allow_html=True)

apply_background()

sleep_duration = 1.0 if os.getenv("STREAMLIT_SERVER_HEADLESS") == "1" else 0.5

# ---------------------------
# ⏳ BLOQUE DE CARGA
# ---------------------------
with st.spinner("Cargando datos y gráficos..."):
    metadata = load_future_metadata()
    player_names = sorted(metadata["Player_name"].dropna().unique())

    selected_player = player_names[0] if player_names else None


# ---------------------------
# 📌 SIDEBAR
# ---------------------------
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

    st.markdown("""
        <h2 style='white-space: nowrap; margin: 0 0 0.5rem 0; color: #ffffff; font-size: 1rem;'>
            ℹ️ ¿Cómo funciona Futpeak?
        </h2>
    """, unsafe_allow_html=True)

    st.info("""
        1. Selecciona un jugador del menú desplegable.  
        2. Visualiza su resumen de carrera y proyección.  
        3. Compara con grupos similares.  
    """)

    selected_player = st.selectbox(
        label="🕤 Selecciona un jugador:",
        options=player_names,
        index=0,
        label_visibility="collapsed"
    )

    # 🔑 Obtener player_id tras selección
    id_series = metadata.loc[metadata["Player_name"] == selected_player, "Player_ID"]
    player_id = id_series.iloc[0] if not id_series.empty else None

    # 🔁 Cargar dinámicamente lo que depende del jugador seleccionado
    img = None
    meta = {}
    summary_df = pd.DataFrame()
    seasonal = group_curve = label = None
    fig_stats = fig_minutes = fig_proj = None

    if player_id:
        try:
            with st.spinner("Cargando datos del jugador..."):
                img_path = get_player_image_path(selected_player, metadata)
                if img_path and img_path.exists():
                    img = Image.open(img_path)
                meta = get_metadata_by_player(selected_player, future=True)
                summary_df = summarize_basic_stats(build_player_df(player_id))
                label, seasonal, group_curve = predict_and_project_player(player_id)
                fig_stats = plot_player_stats(player_id)
                fig_minutes = plot_minutes_per_year(player_id)
                fig_proj = plot_rating_projection(selected_player, seasonal, group_curve, label)
                time.sleep(sleep_duration)
        except Exception as e:
            st.error(f"❌ Error al cargar datos del jugador: {e}")
            st.stop()

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

# ---------------------------
# 🏠 CONTENIDO PRINCIPAL
# ---------------------------
st.markdown("""
    <h1 style="font-size:2rem; margin-bottom:0.5rem;">🏟️ ¡Bienvenido a Futpeak!</h1>
    <p style='font-size:1.3rem; line-height:1.5;'>
      Futpeak es una herramienta de scouting que te ayuda a evaluar y proyectar el potencial  
      de jóvenes futbolistas basándose en datos de trayectorias profesionales similares.
    </p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.7, 1, 1.8], gap="medium")

with col1:
    if img:
        st.image(img, use_container_width=True)
    else:
        st.info("⚠️ Imagen no disponible para este jugador.")

    if meta:
        raw_age = str(meta.get("Age", "N/A"))
        age_display = raw_age.split("-")[0] if "-" in raw_age else raw_age
        minutos = int(summary_df['Minutos totales'].iloc[0]) if not summary_df.empty else "N/A"
        st.markdown(f"""
        <div class='block-card'>
            <h3>📋 Perfil del jugador</h3>
            <p><strong>Nombre:</strong> {selected_player}</p>
            <p><strong>Edad:</strong> {age_display}</p>
            <p><strong>Posición:</strong> {meta.get('Position', 'N/A')}</p>
            <p><strong>Minutos jugados:</strong> {minutos}</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 Producción Ofensiva")
    if fig_stats:
        st.pyplot(fig_stats)
    else:
        st.warning("⚠️ No se pudo generar esta gráfica.")

    st.markdown("### ⏱️ Minutos por Año")
    if fig_minutes:
        fig_minutes.set_size_inches(6, 3)
        st.pyplot(fig_minutes)
    else:
        st.warning("⚠️ No se pudo generar esta gráfica.")

with col3:
    st.markdown("### 📈 Predicción de grupo y evolución")
    if fig_proj:
        fig_proj.set_size_inches(6, 4)
        st.pyplot(fig_proj)
    else:
        st.warning("⚠️ No se pudo generar esta gráfica.")

# ---------------------------
# 🔮 CONCLUSIONES
# ---------------------------
if player_id:
    try:
        conclusion_text = generar_conclusion_completa(player_id).replace("## ", "")
        st.markdown(f"""
        <div class='block-card'>
          <h3>🌠 Conclusiones</h3>
          <p style="font-size:20px; line-height:1.4;">
            {conclusion_text}
          </p>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error generando conclusión: {e}")
