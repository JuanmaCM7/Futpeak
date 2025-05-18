from typing import Tuple
from pandas import DataFrame
import pandas as pd
from data_loader import load_future_matchlogs, load_future_metadata
from analytics import compute_rating_row

def build_player_df(player_id: str) -> DataFrame:
    matchlogs = load_future_matchlogs()
    metadata = load_future_metadata()

    player_df = matchlogs[matchlogs["Player_ID"] == player_id].copy()
    meta_row = metadata[metadata["Player_ID"] == player_id].copy()

    if player_df.empty or meta_row.empty:
        raise ValueError("Jugador no encontrado en los datos.")

    player_df["Date"] = pd.to_datetime(player_df["Date"], errors="coerce")
    meta_row["Birth_date"] = pd.to_datetime(meta_row["Birth_date"], errors="coerce")

    player_df = player_df.merge(meta_row[["Player_ID", "Birth_date"]], on="Player_ID", how="left")
    player_df["Age"] = (player_df["Date"] - player_df["Birth_date"]).dt.days / 365.25
    return player_df

def calculate_rating_per_90(player_df: DataFrame) -> DataFrame:
    rating_cols = ['Goals', 'Assists', 'Shots', 'Shots_on_target', 'Yellow_cards', 'Red_cards', 'Minutes']
    player_df[rating_cols] = player_df[rating_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    player_df["rating_per_90"] = player_df.apply(compute_rating_row, axis=1)
    return player_df

def summarize_basic_stats(player_df: DataFrame) -> DataFrame:
    numeric_cols = ['Goals', 'Assists', 'Minutes', 'Yellow_cards', 'Red_cards']
    player_df[numeric_cols] = player_df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    total_matches = len(player_df)
    total_minutes = player_df["Minutes"].sum()
    total_goals = player_df["Goals"].sum()
    total_assists = player_df["Assists"].sum()
    total_ga = total_goals + total_assists
    total_yellows = player_df["Yellow_cards"].sum()
    total_reds = player_df["Red_cards"].sum()

    goals_per_90 = total_goals / (total_minutes / 90) if total_minutes > 0 else 0
    assists_per_90 = total_assists / (total_minutes / 90) if total_minutes > 0 else 0
    ga_per_90 = total_ga / (total_minutes / 90) if total_minutes > 0 else 0

    return pd.DataFrame({
        "Total partidos": [total_matches],
        "Minutos totales": [total_minutes],
        "Goles": [total_goals],
        "Asistencias": [total_assists],
        "G+A": [total_ga],
        "Amarillas": [total_yellows],
        "Rojas": [total_reds],
        "Goles/90": [goals_per_90],
        "Asistencias/90": [assists_per_90],
        "G+A/90": [ga_per_90],
    })

def build_annual_profile(player_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # 1. Añadir columna de año natural
    player_df['Calendar_year'] = player_df['Date'].dt.year

    # 2. Detectar año de debut
    debut_year = player_df[player_df['Minutes'] > 0]['Calendar_year'].min()
    player_df['year_since_debut'] = player_df['Calendar_year'] - debut_year + 1

    # 3. Agregación por año desde debut
    career_df = player_df.groupby('year_since_debut').agg({
        'Minutes': 'sum',
        'Goals': 'sum',
        'Assists': 'sum',
        'rating_per_90': 'mean',
        'Age': 'mean'
    }).reset_index()

    # 4. Pivotar años a columnas
    pivot_rating = career_df.pivot(columns='year_since_debut', values='rating_per_90')
    pivot_age = career_df.pivot(columns='year_since_debut', values='Age')
    pivot_minutes = career_df.pivot(columns='year_since_debut', values='Minutes')

    # 5. Renombrar columnas
    pivot_rating.columns = [f'rating_year_{i}' for i in pivot_rating.columns]
    pivot_age.columns = [f'age_year_{i}' for i in pivot_age.columns]
    pivot_minutes.columns = [f'minutes_year_{i}' for i in pivot_minutes.columns]

    # 6. Unir todo
    player_model_df = pd.concat([pivot_rating, pivot_age, pivot_minutes], axis=1)

    # 7. Variables derivadas
    if 'rating_year_2' in player_model_df and 'rating_year_1' in player_model_df:
        player_model_df['growth_2_1'] = player_model_df['rating_year_2'] - player_model_df['rating_year_1']
    if 'rating_year_3' in player_model_df and 'rating_year_2' in player_model_df:
        player_model_df['growth_3_2'] = player_model_df['rating_year_3'] - player_model_df['rating_year_2']

    player_model_df['avg_rating'] = player_model_df[[c for c in player_model_df.columns if 'rating_year_' in c]].mean(axis=1)
    player_model_df['sum_minutes'] = player_model_df[[c for c in player_model_df.columns if 'minutes_year_' in c]].sum(axis=1)

    if 'rating_year_3' in player_model_df and 'rating_year_1' in player_model_df:
        player_model_df['rating_trend'] = player_model_df['rating_year_3'] - player_model_df['rating_year_1']
    if 'minutes_year_3' in player_model_df and 'minutes_year_1' in player_model_df:
        player_model_df['minutes_trend'] = player_model_df['minutes_year_3'] - player_model_df['minutes_year_1']

    # 8. Factor de fiabilidad opcional (si fue entrenado con esto)
    for i in [1, 2, 3]:
        min_col = f'minutes_year_{i}'
        if min_col in player_model_df.columns:
            player_model_df[f'minutes_weight_{i}'] = player_model_df[min_col].clip(0, 600) / 600

    # 9. Devolver estructura esperada
    return player_model_df, career_df



def aggregate_stats_by_year(player_df: DataFrame) -> DataFrame:
    if "year_since_debut" not in player_df.columns:
        player_df["Natural_year"] = player_df["Date"].dt.year
        debut_year = player_df[player_df["Minutes"] > 0]["Natural_year"].min()
        player_df["year_since_debut"] = player_df["Natural_year"] - debut_year + 1

    stats = player_df.groupby("year_since_debut").agg({
        "Goals": "sum",
        "Assists": "sum",
        "Minutes": "sum",
        "Date": "count"
    }).rename(columns={"Date": "Matches"}).reset_index()

    stats["G+A"] = stats["Goals"] + stats["Assists"]
    return stats