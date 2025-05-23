from gemini_utils import generar_conclusion_gemini
from model_runner import predict_and_project_player
from data_loader import load_future_metadata
from player_processing import build_player_df
from datetime import datetime
import pandas as pd

def generar_conclusion_completa(player_id: str) -> str:
    fecha_actual = datetime(2025, 5, 23)
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
Informe de Scouting: {player_name} – {fecha_str}

Clasificación del modelo: {group_label}

El jugador debutó en {debut_year} con {debut_minutes} minutos y {debut_ga} goles + asistencias.  
Ese primer año, a pesar de la baja participación, mostró eficacia: aportó en pocos minutos, reflejando un buen nivel de adaptación.

Desde entonces, su progresión ha sido constante.  
En {peak_year}, alcanzó su año más productivo con {peak_ga} goles + asistencias en {peak_minutes} minutos.  
Actualmente ({current_year}), está sumando {current_minutes} minutos y {current_ga} G+A, lo que indica que **está cuajando una temporada sólida y de impacto ofensivo**.

Su curva de evolución, especialmente en producción ofensiva y carga de minutos, refleja un perfil **en crecimiento**.  
En términos de rendimiento global, su desarrollo comparado con el grupo proyectado es **{comparativa} la media**, lo que sugiere que puede consolidarse como un jugador diferencial si mantiene esta línea.

El rating a lo largo de los años ha mostrado subidas y bajadas, pero no debe interpretarse de forma aislada:  
- En su debut, el alto rating respondió a una **gran eficacia con pocos minutos**.  
- En temporadas de mayor carga, el impacto ofensivo ha crecido, aunque el rating puede haberse estabilizado por el rol más exigente o nuevas responsabilidades.

🎯 En resumen, es un perfil que combina crecimiento, adaptación progresiva y eficacia ofensiva.  
Para confirmar su proyección, será clave evaluar su evolución en consistencia y aportar con regularidad.  
Se recomienda un seguimiento continuo y análisis tácticos detallados para confirmar su tendencia positiva a largo plazo.
"""

    return generar_conclusion_gemini(prompt, temperature=0.25)