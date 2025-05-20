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

player_conclusions_by_id = {
    "9e7483ff": (
        "Según nuestro modelo, Désiré Doué no solo ha superado en 2024 la media de su grupo "
        "de “jóvenes estrellas”, sino que también ha superado la trayectoria de proyección "
        "ajustada. Tras un sobresaliente debut en 2021, sufrió una caída en 2022 mientras acumulaba "
        "más minutos, pero en 2023 y especialmente en 2024 recuperó y superó tanto la evolución "
        "esperada como el rendimiento promedio de su grupo. 2024 se perfila como su año de máximo "
        "rendimiento ofensivo."
    ),
    "5b92d896": (
        "Hugo Ekitike comenzó tímido en 2020, pero en 2021 despuntó con un rating cercano a 5.5, "
        "muy por encima de su grupo de “jóvenes estrellas”. En 2022 vivió una fase de estabilización "
        "mientras seguía ganando minutos, y en 2023 regresó al alza, consolidándose como referente. "
        "Nuestro modelo proyecta que en 2024 mantendrá un rendimiento superior a la media de su grupo "
        "y que podrá seguir en esa línea hasta al menos 2026."
    ),
    "2c0558b8": (
        "Jamal Musiala ha mostrado un crecimiento casi lineal desde su debut en 2018, alcanzando su "
        "pico en 2022 con un rating de 5.0, muy por encima de sus pares. Aunque la proyección ajustada "
        "anticipa un leve descenso tras 2023, su curva se mantiene siempre por encima de la media de “jóvenes "
        "estrellas”. Su año de máximo rendimiento fue 2022, y se espera que siga liderando a nivel ofensivo "
        "hasta 2025."
    ),
    "a2728fbf": (
        "Endrick debutó en 2022 y sorprendió con un rating próximo a 6.0 en su primer año, muy por encima "
        "de su grupo. En 2023 vio cómo su rendimiento caía ligeramente al ganar experiencia y minutos, pero en 2024 "
        "recuperó fuerza y volvió a situarse por encima de la proyección ajustada. Nuestro modelo indica que su "
        "peak year podría ser 2025, y que mantendrá un rendimiento destacado frente a sus pares."
    ),
    "633b2b1f": (
        "Franco Mastantuono debutó en 2021 con un rating destacado superior a 4.5. En 2022 mantuvo ese nivel, "
        "pero en 2023 bajó ligeramente hacia la media de su grupo mientras acumulaba más minutos. En 2024 ha mostrado "
        "un repunte modesto que le sitúa justo en la proyección ajustada. Según nuestro modelo, su peak year "
        "será 2024 y podría mantenerse estable hasta 2026."
    ),
    "82ec26c1": (
        "Lamine Yamal irrumpió en 2022 con un rendimiento sólido, logrando un rating de 4.2, muy por encima de su "
        "grupo medio. En 2023 superó incluso la trayectoria proyectada y en 2024 se consolidó como una de las jóvenes "
        "estrellas con mejor progresión. La proyección ajustada sugiere que mantendrá un nivel alto hasta al menos 2026, "
        "con su peak year en 2024."
    ),
    "829aa60c": (
        "Mathys Tel mostró un inicio prometedor en 2021, con un rating cercano a 5.0, superando a su grupo de “jóvenes "
        "estrellas”. En 2022 y 2023 vivió fases de ajuste bajando hacia la media, aunque acumuló minutos clave. "
        "En 2024 recuperó impulso y ha vuelto a situarse sobre la proyección ajustada. Nuestro modelo prevé que su "
        "mejor año será 2025, manteniendo buen ritmo hasta 2027."
    ),
    "6b9960cf": (
        "Warren Zaire-Emery debutó en 2021 con un rating aún incipiente, pero en 2022 dio un salto de calidad que lo posicionó"
        "por encima de la media de su grupo de “jugadores medios”. A lo largo de 2023 y 2024, su evolución se estabilizó"
        "en torno a la proyección ajustada, mostrando consistencia, madurez táctica y fiabilidad en entornos competitivos."
        "Según nuestro modelo, su peak year llegará en 2025, y se espera que mantenga un rendimiento sostenido hasta al menos 2027."
    ),
}


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

# Sidebar: logo, instrucciones y selector de jugador
with st.sidebar:
    # Logo Futpeak
    logo_path = Path(__file__).parent / "assets" / "logo_no_bg_preview_3.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"<div class='fixed-logo-wrapper'><img class='fixed-logo' src='data:image/png;base64,{encoded}'/></div>",
            unsafe_allow_html=True
        )

    # Espacio superior
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # Título personalizado (sin salto de línea)
    st.markdown(
        """
        <h2 style='
            white-space: nowrap;
            margin: 0 0 0.5rem 0;
            color: #FFD700;
            font-size: 1rem;
        '>
            ℹ️ ¿Cómo funciona Futpeak?
        </h2>
        """,
        unsafe_allow_html=True
    )

    # Instrucciones
    st.info("""
        1. Selecciona un jugador del menú desplegable.  
        2. Visualiza al instante su resumen de carrera y proyección.  
        3. Compara con grupos de jugadores similares.  
    """)

    # Selector de jugador sin label interno
    metadata = load_future_metadata()
    player_names = sorted(metadata["Player_name"].dropna().unique())

    # Etiqueta fuera del select, valor colapsado
    st.markdown(
        "<p style='margin:0 0 0.25rem 0; white-space: nowrap; color:#FFD700; font-size:1rem;'>"
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
    /* ✅ OPCIONES DESPLEGADAS: todas en negro */
    div[data-baseweb="menu"] [role="option"] {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

    id_series = metadata.loc[metadata["Player_name"] == selected_player, "Player_ID"]
    player_id = id_series.iloc[0] if not id_series.empty else None
    # Nota informativa en desarrollo
    st.markdown(
        """
        <p style="
        font-size: 0.85rem;
        color: #CCCCCC;
        margin-top: 0.5rem;
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
# Título principal
st.markdown(
    """
    # 🏟️ ¡Bienvenido a Futpeak!
    <p style='font-size:1.3rem; line-height:1.5;'>
      Futpeak es una herramienta de scouting que te ayuda a evaluar y proyectar el potencial  
      de jóvenes futbolistas basándose en datos de jugadores con trayectorias profesionales similares.
    </p>
    """,
    unsafe_allow_html=True
)

# Estructura de columnas: mantenemos ratio original (0.5, 1, 1.8)
col1, col2, col3 = st.columns([0.7, 1, 1.8], gap="large")

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

        # Obtener y acortar la edad (antes del guión)
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
        label, seasonal, group_curve = predict_and_project_player(player_id)
        player_name = metadata.loc[metadata["Player_ID"] == player_id, "Player_name"].values[0]
        fig_proj = plot_rating_projection(player_name, seasonal, group_curve, label)
        # Reducimos el tamaño de la figura dentro de la columna
        fig_proj.set_size_inches(6, 4)
        st.pyplot(fig_proj)
    else:
        st.warning("⚠️ Selecciona un jugador para ver la proyección.")

# Obtengo la conclusión
conclusion_text = player_conclusions_by_id.get(
    player_id,
    "No hay una conclusión específica para este jugador."
)

# Inserto un <p> con estilo inline para aumentar el tamaño
st.markdown(
    f"""
    <div class='block-card'>
      <h3>🔮 Conclusiones</h3>
      <p style="font-size:20px; line-height:1.4;">
        {conclusion_text}
      </p>
    </div>
    """,
    unsafe_allow_html=True
)