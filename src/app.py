# app.py
import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import os

from data_loader import load_future_metadata, get_metadata_by_player, get_matchlogs_by_player, get_player_image_path, get_name_id_mapping
from model_runner import predict_and_project_player
from stats import plot_player_stats
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
                .fixed-logo-wrapper {{
                    width: 100%;
                    padding: 0;
                    margin: 0 0 -1.2rem 0;
                    display: block;
                    position: relative;
                }}
                .fixed-logo {{
                    width: 240px;
                    height: auto;
                    display: block;
                    margin-left: 0;
                    margin-top: -15px;
                }}
            </style>
            <div class="fixed-logo-wrapper">
                <img class="fixed-logo" src="data:image/png;base64,{encoded_logo}" alt="Futpeak Logo">
            </div>
        """, unsafe_allow_html=True)
    st.markdown("------")
    st.markdown("### ℹ️ How to use Futpeak", unsafe_allow_html=True)
    st.info("""
    1. Select a player from the dropdown.
    2. Instantly view their career summary and projection.
    3. Compare against similar player groups.
    """)

    st.markdown("## 👤 Player Selector", unsafe_allow_html=True)
    metadata = load_future_metadata()
    player_names = sorted(metadata["Player_name"].dropna().unique())
    selected_player = st.selectbox("Choose a player", player_names, index=0)

    st.markdown("#### 🛠 Filters (soon)", unsafe_allow_html=True)
    st.caption("You’ll be able to filter by age, position, minutes, injury history and more.")

# Título principal
st.markdown("""
    <div style='margin-top: -40px;'>
        <h1 style='font-size: 2.5rem;'>🏟️ Welcome to Futpeak</h1>
        <p style='font-size: 1.1rem;'>Futpeak is a scouting tool that helps you evaluate and project the potential of young footballers based on data from players with similar career paths.</p>
    </div>
""", unsafe_allow_html=True)

# Cuerpo dividido en columnas horizontales (3 secciones)
col1, col2, col3 = st.columns([0.5, 1, 1.8], gap="large")


# --- Columna 1 y 2: Imagen del jugador y Perfil del jugador
from pathlib import Path

with col1:
    st.markdown("### 🖼️ Player Image")
    
    img_path = get_player_image_path(selected_player)

    if img_path:
        img = Image.open(img_path)
        st.image(img, use_column_width=True)
    else:
        st.info("⚠️ Imagen no disponible para este jugador.")

    if selected_player:
        meta = get_metadata_by_player(selected_player, future=True)
        profile_html = f"""
        <div class="block-card" style="margin-top: 20px; padding: 1rem 1rem;">
            <h3>📋 Player Profile</h3>
            <p><strong>Nombre:</strong> {selected_player}</p>
            <p><strong>Edad:</strong> {meta.get('Age', 'N/A')}</p>
            <p><strong>Posición:</strong> {meta.get('Position', 'N/A')}</p>
            <p><strong>Minutos jugados:</strong> —</p>
            <p><strong>Historial de lesiones:</strong> —</p>
        </div>
        """
        st.markdown(profile_html, unsafe_allow_html=True)



with col2:
    # Añadimos gráfico de estadísticas (G+A)
    st.markdown("""
        <div style='margin-top: 1.5rem;'>
            <h4>📊 Producción Ofensiva</h4>
        </div>
    """, unsafe_allow_html=True)

    fig_stats = plot_player_stats(selected_player)
    if fig_stats:
        st.pyplot(fig_stats)
    else:
        st.markdown("⚠️ No hay datos suficientes para mostrar estadísticas ofensivas.")


    st.markdown("</div>", unsafe_allow_html=True)


# --- Columna 3: Rating Evolution + Stats
with col3:
    st.markdown("""
        <div class="block-card" style="max-width: 80%; margin-top: -0.5rem; padding: 1.2rem;">
            <h3 style="margin-bottom: 1rem;">📈 Rating Evolution</h3>
    """, unsafe_allow_html=True)

    predicted_label, player_seasonal, group_curve = predict_and_project_player(selected_player)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 3.5), constrained_layout=True)

    ax.plot(
        player_seasonal['year_since_debut'],
        player_seasonal['rating_per_90'],
        marker='o', markersize=8, linewidth=2.5,
        color="#0066cc", label=selected_player
    )
    ax.plot(
        group_curve['year_since_debut'],
        group_curve['rating_avg'],
        linestyle='--', linewidth=2,
        color="#ffa726", label=f"Grupo promedio: {predicted_label}"
    )
    ax.plot(
        group_curve['year_since_debut'],
        group_curve['projection'],
        linestyle=':', linewidth=2,
        color="#2e7d32", label="Proyección ajustada"
    )

    ax.set_title(f"📈 Evolución y proyección de {selected_player}", fontsize=14, weight='bold')
    ax.set_xlabel("Años desde el debut", fontsize=12)
    ax.set_ylabel("Rating por 90 minutos", fontsize=12)
    ax.tick_params(axis='both', labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='lower center', fontsize=10)
    fig.tight_layout()
    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)



# Conclusión textual
with st.container():
    st.markdown("""
    <div class="block-card">
        <h3>🔮 Career Projection Insight</h3>
        <p>Según el análisis de trayectoria, este jugador muestra un crecimiento sostenido en los primeros años con potencial de mantenerse por encima de la media de su grupo. Ajustado a minutos jugados y edad, su evolución es positiva.</p>
    </div>
    """, unsafe_allow_html=True)