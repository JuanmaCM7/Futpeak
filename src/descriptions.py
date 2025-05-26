from model_runner import predict_and_project_player
from data_loader import load_future_metadata
from player_processing import build_player_df
from datetime import datetime
import pandas as pd
import requests
import streamlit as st

@st.cache_data
def generar_prompt_conclusion(player_id: str) -> str:
    fecha_actual = datetime.now()
    fecha_str = fecha_actual.strftime("%d de %B de %Y").lstrip("0").capitalize()

    # Modelo y metadatos
    group_label, seasonal_df, group_curve = predict_and_project_player(player_id)
    metadata = load_future_metadata()
    player_name = metadata[metadata["Player_ID"] == player_id]["Player_name"].values[0]

    # Matchlogs
    matchlogs = build_player_df(player_id)
    matchlogs = matchlogs[matchlogs["Minutes"] > 0].sort_values("Date")
    debut_year = pd.to_datetime(matchlogs.iloc[0]["Date"]).year

    # Datos por temporada
    seasonal_df = seasonal_df.sort_values("year_since_debut")
    seasonal_df["Minutes"] = pd.to_numeric(seasonal_df["Minutes"], errors="coerce")
    seasonal_df["Goals"] = pd.to_numeric(seasonal_df.get("Goals", 0), errors="coerce")
    seasonal_df["Assists"] = pd.to_numeric(seasonal_df.get("Assists", 0), errors="coerce")
    seasonal_df["G+A"] = seasonal_df["Goals"] + seasonal_df["Assists"]
    seasonal_df["rating_per_90"] = pd.to_numeric(seasonal_df["rating_per_90"], errors="coerce")

    # Año debut
    debut_row = seasonal_df[seasonal_df["year_since_debut"] == 1].iloc[0]
    debut_minutes = int(debut_row["Minutes"])
    debut_ga = int(debut_row["G+A"])
    debut_rating = debut_row["rating_per_90"]

    # Año más productivo
    peak_prod_row = seasonal_df.loc[seasonal_df["G+A"].idxmax()]
    peak_year = debut_year + int(peak_prod_row["year_since_debut"]) - 1
    peak_ga = int(peak_prod_row["G+A"])
    peak_minutes = int(peak_prod_row["Minutes"])
    peak_rating = peak_prod_row["rating_per_90"]

    # Año actual
    current_row = seasonal_df[seasonal_df["year_since_debut"] == seasonal_df["year_since_debut"].max()].iloc[0]
    current_year = debut_year + int(current_row["year_since_debut"]) - 1
    current_ga = int(current_row["G+A"])
    current_minutes = int(current_row["Minutes"])
    current_rating = current_row["rating_per_90"]

    # Curva comparativa
    curva_jugador = seasonal_df.set_index("year_since_debut")["rating_per_90"]
    curva_grupo = group_curve.set_index("year_since_debut")["rating_avg"]
    comparativa = "por encima" if (curva_jugador - curva_grupo).mean() > 0.15 else "en línea con"

    # Prompt final
    prompt = f"""
    🧠 Genera un informe de scouting realista y detallado para el jugador {player_name}, basado en los siguientes datos.  
    El informe debe ser honesto: si el rendimiento es bajo, se debe reflejar. Si hay signos de estancamiento, menciona eso. No des por hecho que todo es positivo. Usa un lenguaje profesional y concreto.

    📅 Fecha del informe: {fecha_str}

    📌 Datos generales:
    - Clasificación del modelo: {group_label}
    - Año de debut: {debut_year}
    - Producción en el debut: {debut_minutes} minutos | {debut_ga} G+A | Rating: {debut_rating:.2f}

    📈 Mejor año:
    - Año: {peak_year}
    - Producción: {peak_minutes} minutos | {peak_ga} G+A | Rating: {peak_rating:.2f}

    📉 Año actual:
    - Año: {current_year}
    - Producción: {current_minutes} minutos | {current_ga} G+A | Rating: {current_rating:.2f}

    📊 Comparativa con su grupo proyectado:
    - Su curva está {comparativa} la media del grupo

    ✍️ Genera un análisis que comente:
    - Cómo ha sido la progresión desde el debut
    - Si hay estancamiento, retroceso o consolidación
    - Qué potencial muestra realmente hoy (sin exagerar)
    - En qué debe mejorar, si hay aspectos preocupantes
    - Si se recomienda seguimiento, fichaje, cesión o precaución

    El estilo debe ser objetivo, claro y útil para un departamento de scouting.
    """
    return prompt

def generar_conclusion_completa(player_id: str) -> str:
    try:
        prompt = generar_prompt_conclusion(player_id)

        response = requests.post(
            "https://JuanmaCM7-gemini-endpoint.hf.space/generate",
            json={"prompt": prompt},
            timeout=30
        )
        result = response.json()
        if "result" in result:
            conclusion = result["result"].replace("**", "")
            return conclusion
        else:
            return f"❌ Error del servidor IA: {result.get('error', 'Respuesta inesperada')}"
    except Exception as e:
        return f"❌ Error al contactar con la IA: {e}"

