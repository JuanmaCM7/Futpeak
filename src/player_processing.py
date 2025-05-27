from typing import Tuple
from pandas import DataFrame
import pandas as pd
from data_loader import load_future_matchlogs, load_future_metadata
from analytics import compute_rating_row
import streamlit as st
import re

@st.cache_data
def build_player_df(player_id: str) -> DataFrame:
    """
    Carga y prepara los datos de matchlogs para un jugador.
    """
    matchlogs = load_future_matchlogs()
    metadata = load_future_metadata()

    player_df = matchlogs[matchlogs["Player_ID"] == player_id].copy()
    meta_row = metadata[metadata["Player_ID"] == player_id].copy()

    if player_df.empty or meta_row.empty:
        raise ValueError(f"Jugador {player_id} no encontrado en los datos.")

    player_df["Date"] = pd.to_datetime(player_df["Date"], errors="coerce")
    player_df["Minutes"] = pd.to_numeric(player_df["Minutes"], errors="coerce").fillna(0)
    player_df["Goals"] = pd.to_numeric(player_df.get("Goals", 0), errors="coerce").fillna(0)
    player_df["Assists"] = pd.to_numeric(player_df.get("Assists", 0), errors="coerce").fillna(0)
    meta_row["Birth_date"] = pd.to_datetime(meta_row["Birth_date"], errors="coerce")

    player_df = player_df.merge(
        meta_row[["Player_ID", "Birth_date"]],
        on="Player_ID", how="left"
    )
    player_df["Age"] = (player_df["Date"] - player_df["Birth_date"]).dt.days / 365.25

    return player_df

def calculate_rating_per_90(player_df: DataFrame) -> DataFrame:
    cols = ['Goals', 'Assists', 'Shots', 'Shots_on_target', 'Yellow_cards', 'Red_cards', 'Minutes']
    player_df[cols] = player_df[cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    player_df["rating_per_90"] = player_df.apply(compute_rating_row, axis=1)
    return player_df

@st.cache_data
def summarize_basic_stats(player_df: DataFrame) -> DataFrame:
    cols = ['Goals', 'Assists', 'Minutes', 'Yellow_cards', 'Red_cards']
    player_df[cols] = player_df[cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    total_matches = len(player_df)
    total_minutes = player_df['Minutes'].sum()
    total_goals = player_df['Goals'].sum()
    total_assists = player_df['Assists'].sum()
    total_ga = total_goals + total_assists
    total_yellows = player_df['Yellow_cards'].sum()
    total_reds = player_df['Red_cards'].sum()

    goals_per_90 = total_goals / (total_minutes / 90) if total_minutes > 0 else 0
    assists_per_90 = total_assists / (total_minutes / 90) if total_minutes > 0 else 0
    ga_per_90 = total_ga / (total_minutes / 90) if total_minutes > 0 else 0

    return pd.DataFrame({
        'Total partidos': [total_matches],
        'Minutos totales': [total_minutes],
        'Goles': [total_goals],
        'Asistencias': [total_assists],
        'G+A': [total_ga],
        'Amarillas': [total_yellows],
        'Rojas': [total_reds],
        'Goles/90': [goals_per_90],
        'Asistencias/90': [assists_per_90],
        'G+A/90': [ga_per_90],
    })

@st.cache_data
def build_annual_profile(player_df: DataFrame) -> Tuple[DataFrame, DataFrame]:
    player_df = calculate_rating_per_90(player_df)
    player_df['Natural_year'] = player_df['Date'].dt.year
    debut_year = player_df.loc[player_df['Minutes'] > 0, 'Natural_year'].min()
    player_df['year_since_debut'] = player_df['Natural_year'] - debut_year + 1

    career_df = player_df.groupby('year_since_debut').agg({
        'Minutes': 'sum',
        'Goals': 'sum',
        'Assists': 'sum',
        'rating_per_90': 'mean',
        'Age': 'mean'
    }).reset_index()

    pivot_rating = (
        career_df
        .set_index('year_since_debut')['rating_per_90']
        .rename(lambda x: f'rating_year_{x}')
        .to_frame().T
        .reset_index(drop=True)
    )

    pivot_age = (
        career_df
        .set_index('year_since_debut')['Age']
        .rename(lambda x: f'age_year_{x}')
        .to_frame().T
        .reset_index(drop=True)
    )

    pivot_minutes = (
        career_df
        .set_index('year_since_debut')['Minutes']
        .rename(lambda x: f'minutes_year_{x}')
        .to_frame().T
        .reset_index(drop=True)
    )

    player_model_df = pd.concat([pivot_rating, pivot_age, pivot_minutes], axis=1)
    print(f"✅ Filas finales en player_model_df: {player_model_df.shape[0]}")

    for col1, col2, new in [
        ('rating_year_2', 'rating_year_1', 'growth_2_1'),
        ('rating_year_3', 'rating_year_2', 'growth_3_2'),
        ('rating_year_3', 'rating_year_1', 'rating_trend'),
        ('minutes_year_3', 'minutes_year_1', 'minutes_trend'),
    ]:
        if col1 in player_model_df.columns and col2 in player_model_df.columns:
            player_model_df[new] = player_model_df[col1] - player_model_df[col2]

    player_model_df['avg_rating'] = player_model_df.filter(like='rating_year_').mean(axis=1)
    player_model_df['sum_minutes'] = player_model_df.filter(like='minutes_year_').sum(axis=1)

    for i in [1, 2, 3]:
        col = f'minutes_year_{i}'
        if col in player_model_df.columns:
            player_model_df[f'minutes_weight_{i}'] = player_model_df[col].clip(0, 600) / 600

    return player_model_df, career_df

@st.cache_data
def aggregate_stats_by_year(player_df: DataFrame) -> DataFrame:
    df = player_df.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce').fillna(0)
    df['Goals'] = pd.to_numeric(df['Goals'], errors='coerce').fillna(0)
    df['Assists'] = pd.to_numeric(df['Assists'], errors='coerce').fillna(0)

    df['Natural_year'] = df['Date'].dt.year
    debut_year = df.loc[df['Minutes'] > 0, 'Natural_year'].min()
    df['year_since_debut'] = df['Natural_year'] - debut_year + 1

    stats = df.groupby('year_since_debut').agg(
        Goals=('Goals','sum'),
        Assists=('Assists','sum'),
        Minutes=('Minutes','sum'),
        Matches=('Date','count')
    ).reset_index()
    stats['G+A'] = stats['Goals'] + stats['Assists']
    return stats

@st.cache_data
def get_player_stats(player_id: str) -> DataFrame:
    df = build_player_df(player_id)
    return aggregate_stats_by_year(df)


