# 📦 src/scripts/stats.py

import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import joblib

from data_loader import get_matchlogs_by_player

def get_player_stats(player_name):
    df = get_matchlogs_by_player(player_name, future=True)
    print("🧪 Filtrado inicial:")
    print(df[['Player_name', 'Minutes', 'Goals', 'Assists', 'Date']].head())
    df = df.copy()

    df['Goals'] = pd.to_numeric(df['Goals'], errors='coerce')
    df['Assists'] = pd.to_numeric(df['Assists'], errors='coerce')
    df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    df = df[df['Minutes'] >= 70]  # 👈 REVISAR UMBRAL

    if df.empty:
        return pd.DataFrame()  # Para prevenir errores

    debut_year = df[df['Minutes'] > 70]['Date'].dt.year.min()
    df['year_since_debut'] = df['Date'].dt.year - df[df['Minutes'] > 0]['Date'].dt.year.min() + 1


    stats = df.groupby('year_since_debut').agg({
        'Goals': 'sum',
        'Assists': 'sum',
        'Minutes': 'sum',
        'Date': 'count'
    }).rename(columns={'Date': 'Matches'}).reset_index()

    stats['G+A'] = stats['Goals'] + stats['Assists']
    return stats



def plot_player_stats(player_name):
    stats = get_player_stats(player_name)
    if stats.empty:
        return None

    # Asegurar tipos antes de graficar
    stats['G+A'] = pd.to_numeric(stats['G+A'], errors='coerce')
    stats['year_since_debut'] = pd.to_numeric(stats['year_since_debut'], errors='coerce')

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4))

    sns.barplot(
        data=stats,
        x='year_since_debut',
        y='G+A',
        color="#42a5f5",
        ax=ax
    )

    ax.set_title(f"G+A por año - {player_name}", fontsize=11, weight='bold')
    ax.set_xlabel("Año desde debut")
    ax.set_ylabel("Goles + Asistencias")
    ax.grid(True, linestyle='--', alpha=0.5)
    fig.tight_layout()
    return fig


