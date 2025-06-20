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
from player_processing import build_player_df, summarize_basic_stats, traducir_posicion
from stats import (
    plot_player_stats,
    plot_minutes_per_year,
    plot_rating_projection
)
from descriptions import generar_conclusion_completa, generar_explicacion_grafica_ga, generar_explicacion_minutos_por_ano, generar_explicacion_curva_evolucion
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

    try:
        metadata = load_future_metadata()
        player_names = sorted(metadata["Player_name"].dropna().unique())
    except Exception as e:
        st.error(f"❌ Error al cargar metadatos: {e}")
        st.stop()

    selected_player = st.selectbox(
        label="🕤 Selecciona un jugador:",
        options=player_names,
        index=0,
        label_visibility="collapsed",
        key="selected_player"
    )

    if "selected_player_prev" not in st.session_state:
        st.session_state.selected_player_prev = selected_player

    if selected_player != st.session_state.selected_player_prev:
        st.session_state.selected_player_prev = selected_player
        st.rerun()


    # Advertencia para modo claro
    st.markdown("""
        <p style="font-size: 0.85rem; background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 6px; margin-top: 8px;">
        ⚠️ Si el selector no se ve correctamente, cambia tu navegador o dispositivo a <strong>modo claro</strong>.
        </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h2 style='white-space: nowrap; margin: 0 0 0.25rem 0; color: #ffffff; font-size: 1rem;'>
        🧙 Consejo
    </h2>
    <div style="background-color: rgba(255, 255, 255, 0.06); padding: 1.25rem 1.25rem 1.2rem 1.25rem; border-radius: 16px; margin-bottom: 1.4rem;">
    <p style="font-size: 0.9rem; color: #ffffff; margin: 0;">
        Pasa el cursor por el icono <span style="color:#ccc; font-weight:bold;">ℹ️</span> junto a cada título de gráfica  
        para obtener una explicación generada por inteligencia artificial.
    </p>
    </div>
    """, unsafe_allow_html=True)


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
# 🏗️ BLOQUE PRINCIPAL
# ---------------------------

placeholder = st.empty()

if selected_player:
    with placeholder.container():
        with st.spinner("🔄 Cargando perfil completo..."):

            player_id = metadata.loc[metadata["Player_name"] == selected_player, "Player_ID"].values[0]

            img = None
            meta = {}
            summary_df = pd.DataFrame()
            seasonal = group_curve = label = None
            fig_stats = fig_minutes = fig_proj = None
            conclusion_text = ""

            try:
                img_path = get_player_image_path(selected_player, metadata)
                if img_path and img_path.exists():
                    img = Image.open(img_path)
            except Exception as e:
                st.warning(f"⚠️ Imagen no disponible: {e}")

            try:
                meta = get_metadata_by_player(selected_player, future=True)
                summary_df = summarize_basic_stats(build_player_df(player_id))
                label, seasonal, group_curve = predict_and_project_player(player_id)
                fig_stats = plot_player_stats(player_id)
                fig_minutes = plot_minutes_per_year(player_id)
                fig_proj = plot_rating_projection(selected_player, seasonal, group_curve, label)
                conclusion_text = generar_conclusion_completa(player_id).replace("## ", "")
            except Exception as e:
                st.warning(f"⚠️ Error durante la carga: {e}")

            time.sleep(sleep_duration)

    placeholder.empty()

    with placeholder.container():
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
                club = meta.get("Club", "N/A")
                age_display = raw_age.split("-")[0] if "-" in raw_age else raw_age
                minutos = int(summary_df['Minutos totales'].iloc[0]) if not summary_df.empty else "N/A"
                st.markdown(f"""
                <div class='block-card' style="
                    min-height: 280px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    line-height: 1.8;
                    padding: 1.8rem 1.5rem;
                ">
                    <h3 style="margin-bottom: 1rem;">📋 Perfil del jugador</h3>
                    <p><strong>Nombre:</strong> {selected_player}</p>
                    <p><strong>Equipo:</strong> {club}</p>
                    <p><strong>Edad:</strong> {age_display}</p>
                    <p><strong>Posición:</strong> {traducir_posicion(meta.get('Position', 'N/A'))}</p>
                    <p><strong>Minutos jugados:</strong> {minutos}</p>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            # 🧠 Generar explicación IA de la gráfica de G+A
            from descriptions import generar_explicacion_grafica_ga
            try:
                explicacion_ia_raw = generar_explicacion_grafica_ga(player_id)
                explicacion_ia = explicacion_ia_raw.replace('"', '').replace('\n', ' ').strip()
            except Exception as e:
                explicacion_ia = "⚠️ No se pudo generar la explicación."

            # 🎨 Estilo tooltip elegante + título con ícono
            st.markdown(f"""
            <style>
            .tooltip-container {{
            position: relative;
            display: inline-block;
            }}

            .tooltip-container .tooltip-text {{
            visibility: hidden;
            max-width: 360px;
            background-color: #333;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            top: 130%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.85rem;
            }}

            .tooltip-container:hover .tooltip-text {{
            visibility: visible;
            opacity: 1;
            }}
            </style>

            <h3 style='display: flex; align-items: center; gap: 6px;'>
            📊 Producción Ofensiva
            <div class="tooltip-container">
                <span style="cursor: help; font-size: 0.9rem; color: #ccc;">ℹ️</span>
                <div class="tooltip-text">{explicacion_ia}</div>
            </div>
            </h3>
            """, unsafe_allow_html=True)

            # 🎯 Mostrar gráfica G+A
            if fig_stats:
                st.pyplot(fig_stats)
            else:
                st.warning("⚠️ No se pudo generar esta gráfica.")

            # ⏱️ Gráfica de minutos
            # 🧠 Explicación IA para minutos por año
            try:
                explicacion_min_raw = generar_explicacion_minutos_por_ano(player_id)
                explicacion_min = explicacion_min_raw.replace('"', '').replace('\n', ' ').strip()
            except Exception as e:
                explicacion_min = "⚠️ No se pudo generar la explicación."

            st.markdown(f"""
            <h3 style='display: flex; align-items: center; gap: 6px;'>
            ⏱️ Minutos por Año
            <div class="tooltip-container">
                <span style="cursor: help; font-size: 0.9rem; color: #ccc;">ℹ️</span>
                <div class="tooltip-text">{explicacion_min}</div>
            </div>
            </h3>
            """, unsafe_allow_html=True)
            if fig_minutes:
                fig_minutes.set_size_inches(6, 3)
                st.pyplot(fig_minutes)
            else:
                st.warning("⚠️ No se pudo generar esta gráfica.")

        with col3:
            # 🧠 Explicación IA para la gráfica de evolución
           
            try:
                explicacion_proj_raw = generar_explicacion_curva_evolucion(player_id)
                explicacion_proj = explicacion_proj_raw.replace('"', '').replace('\n', ' ').strip()
            except Exception as e:
                explicacion_proj = "⚠️ No se pudo generar la explicación."

            # 🎨 Título con tooltip para curva de evolución
            st.markdown(f"""
            <style>
            .tooltip-container {{
            position: relative;
            display: inline-block;
            }}

            .tooltip-container .tooltip-text {{
            visibility: hidden;
            width: 300px;
            background-color: #333;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            top: 130%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.85rem;
            line-height: 1.5;
            white-space: normal;
            word-wrap: break-word;
            }}

            .tooltip-container:hover .tooltip-text {{
            visibility: visible;
            opacity: 1;
            }}
            </style>

            <h3 style='display: flex; align-items: center; gap: 6px;'>
            📈 Predicción de grupo y evolución
            <div class="tooltip-container">
                <span style="cursor: help; font-size: 0.9rem; color: #ccc;">ℹ️</span>
                <div class="tooltip-text">{explicacion_proj}</div>
            </div>
            </h3>
            """, unsafe_allow_html=True)

            if fig_proj:
                fig_proj.set_size_inches(6, 4)
                st.pyplot(fig_proj)
            else:
                st.warning("⚠️ No se pudo generar esta gráfica.")


        if conclusion_text:
            st.markdown(f"""
            <div class='block-card'>
              <h3>🌠 Conclusiones</h3>
              <p style="font-size:20px; line-height:1.4;">
                {conclusion_text}
              </p>
            </div>
            """, unsafe_allow_html=True)
