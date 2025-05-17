# app.py
import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components
import base64
import pandas as pd
import matplotlib.pyplot as plt

from data_loader import load_future_metadata, get_metadata_by_player, get_matchlogs_by_player, get_player_image_path
from model_runner import prepare_features, predict_peak_group, get_curve_by_group, predict_and_project_player
from styles.theme import apply_background

# Configuración general y estilos
st.set_page_config(page_title="Futpeak", layout="wide", initial_sidebar_state="expanded")
apply_background()

# Estilos CSS personalizados
css_path = Path(__file__).parent / "styles" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Ajuste de margen superior
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

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

# Contenido principal
st.title("🏟️ Welcome to Futpeak")
st.markdown("""
Futpeak is a scouting tool that helps you evaluate and project the potential of young footballers based on data from players with similar career paths.
""")

# Layout principal con columnas
with st.container():
    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    with col1:
        if selected_player:
            meta = get_metadata_by_player(selected_player, future=True)
            img_path = get_player_image_path(selected_player)

            profile_html = f"""
            <div class="block-card">
                <h3>📋 Player Profile</h3>
                <p>Nombre: <strong>{selected_player}</strong></p>
                <p>Edad: {meta.get('Age', 'N/A')}</p>
                <p>Posición: {meta.get('Position', 'N/A')}</p>
                <p>Minutos jugados: —</p>
                <p>Historial de lesiones: —</p>
            </div>
            """
            st.markdown(profile_html, unsafe_allow_html=True)

            if img_path:
                st.image(str(img_path), width=200)

    with col2:
        st.markdown("""
        <div class="block-card">
            <h3>📈 Rating Evolution</h3>
        """, unsafe_allow_html=True)

        predicted_label, player_seasonal, group_curve = predict_and_project_player(selected_player)

        # Plot personalizado bonito
        import seaborn as sns
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(7.5, 4.5))

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

        ax.set_title(f"📈 Evolución y proyección de {selected_player}", fontsize=16, weight='bold')
        ax.set_xlabel("Años desde el debut", fontsize=12)
        ax.set_ylabel("Rating por 90 minutos", fontsize=12)
        ax.tick_params(axis='both', labelsize=10)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='lower left', fontsize=10)
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
