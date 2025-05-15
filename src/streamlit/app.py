# app.py
import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components
import base64
from styles.theme import apply_background

# Configuración y fondo
st.set_page_config(page_title="Futpeak", layout="wide", initial_sidebar_state="expanded")
apply_background()

# Estilos CSS personalizados
css_path = Path(__file__).parent / "styles" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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


    # Mini instrucciones rápidas
    st.markdown("### ℹ️ How to use Futpeak", unsafe_allow_html=True)
    st.info("""
    1. Select a player from the dropdown.
    2. Instantly view their career summary and projection.
    3. Compare against similar player groups.
    """)

    # Selector
    st.markdown("## 👤 Player Selector", unsafe_allow_html=True)
    selected_player = st.selectbox("Choose a player", ["Young Prospect"], index=0)

    # (Espacio para futuros filtros)
    st.markdown("#### 🛠 Filters (soon)", unsafe_allow_html=True)
    st.caption("You’ll be able to filter by age, position, minutes, injury history and more.")

    
# Contenido principal
st.title("🏟️ Welcome to Futpeak")
st.markdown("""
Futpeak is a scouting tool that helps you evaluate and project the potential of young footballers based on data from players with similar career paths.
""")

# --- Layout principal con contenedores y columnas ---
with st.container():
    st.markdown("---")  # Separador visual

    # Diseño dividido en 2 columnas
    col1, col2 = st.columns([1, 2])  # proporción 1:2

    with col1:
        player_info_html = """
        <div class="block-card">
            <h3>📋 Player Profile</h3>
            <p>Nombre: <strong>Lamine Yamal</strong></p>
            <p>Edad: 17 años</p>
            <p>Posición: Extremo</p>
            <p>Minutos jugados: 1500</p>
            <p>Historial de lesiones: Ninguna</p>
        </div>
        """
        st.markdown(player_info_html, unsafe_allow_html=True)

        player_img_path = Path("assets/players/young_prospect.png")
        if player_img_path.exists():
            st.image(str(player_img_path), width=200)

    with col2:
        evolution_html = """
        <div class="block-card">
            <h3>📈 Rating Evolution</h3>
            <p><em>Aquí irá el gráfico de evolución</em></p>
        </div>
        """
        st.markdown(evolution_html, unsafe_allow_html=True)

# Conclusión textual
with st.container():
    projection_html = """
    <div class="block-card">
        <h3>🔮 Career Projection Insight</h3>
        <p>Según el análisis de trayectoria, este jugador muestra un crecimiento sostenido en los primeros años con potencial de mantenerse por encima de la media de su grupo. Ajustado a minutos jugados y edad, su evolución es positiva.</p>
    </div>
    """
    st.markdown(projection_html, unsafe_allow_html=True)


