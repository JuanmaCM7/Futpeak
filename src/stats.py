import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from data_loader import get_matchlogs_by_player, get_metadata_by_player

def get_player_stats(player_id):
    df = get_matchlogs_by_player(player_id=player_id, future=True)
    df = df.copy()

    df['Goals'] = pd.to_numeric(df['Goals'], errors='coerce')
    df['Assists'] = pd.to_numeric(df['Assists'], errors='coerce')
    df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    if df.empty:
        return pd.DataFrame()

    df['Natural_year'] = df['Date'].dt.year
    debut_year = df[df['Minutes'] > 0]['Natural_year'].min()
    df['year_since_debut'] = df['Natural_year'] - debut_year + 1

    stats = df.groupby('year_since_debut').agg({
        'Goals': 'sum',
        'Assists': 'sum',
        'Minutes': 'sum',
        'Date': 'count'
    }).rename(columns={'Date': 'Matches'}).reset_index()

    stats['G+A'] = stats['Goals'] + stats['Assists']

    return stats

def plot_player_stats(player_id):
    stats = get_player_stats(player_id)
    player_name = get_metadata_by_player(player_id, future=True).get("Player_name", player_id)

    if stats is None or stats.empty:
        print(f"[DEBUG] No stats disponibles para {player_name}")
        return None

    required_cols = {'G+A', 'year_since_debut'}
    if not required_cols.issubset(stats.columns):
        print(f"[DEBUG] Columnas faltantes en stats: {stats.columns}")
        return None

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

def plot_minutes_per_year(player_id) -> plt.Figure:
    """
    Bar chart de minutos totales por año desde el debut.
    """
    import pandas as pd
    from player_processing import build_player_df, aggregate_stats_by_year
    from data_loader import get_metadata_by_player

    # 1) Agrupamos los datos igual que en G+A
    df = build_player_df(player_id)
    stats_df = aggregate_stats_by_year(df)

    # 2) Nombre para título
    meta = get_metadata_by_player(player_id)
    player_name = meta.get("Player_name", player_id)

    if stats_df is None or stats_df.empty:
        return None

    # 3) Tipos seguros
    stats_df = stats_df.copy()
    stats_df["year_since_debut"] = stats_df["year_since_debut"].astype(int)
    stats_df["Minutes"] = stats_df["Minutes"].astype(float)

    # 4) Plot
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(
        data=stats_df,
        x="year_since_debut",
        y="Minutes",
        color="#66bb6a",
        ax=ax
    )
    ax.set_title(f"Minutos por año - {player_name}", fontsize=11, weight="bold")
    ax.set_xlabel("Año desde debut")
    ax.set_ylabel("Minutos jugados")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig

def plot_rating_projection(player_name: str, player_seasonal: pd.DataFrame, group_curve: pd.DataFrame, pred_label: str):
    sns.set_theme(style="whitegrid")

    # 🔎 Diagnóstico
    print("📊 [DEBUG] player_seasonal:")
    print(player_seasonal[['year_since_debut', 'rating_per_90']].head())

    print("📊 [DEBUG] group_curve:")
    print(group_curve[['year_since_debut', 'rating_avg', 'projection']].head())

    print("🎯 Grupo recibido:", pred_label)
    print("🎯 Grupos disponibles en curvas:", group_curve['peak_group'].unique() if 'peak_group' in group_curve else 'N/A')

    player_seasonal['year_since_debut'] = pd.to_numeric(player_seasonal['year_since_debut'], errors='coerce')
    group_curve['year_since_debut'] = pd.to_numeric(group_curve['year_since_debut'], errors='coerce')

    player_filtered = player_seasonal[player_seasonal['year_since_debut'] <= 13]
    group_filtered = group_curve[
    (group_curve['year_since_debut'] <= 13) &
    (group_curve['rating_avg'].notna()) &
    (group_curve['projection'].notna())
]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        player_filtered['year_since_debut'],
        player_filtered['rating_per_90'],
        marker='o', markersize=8, linewidth=2.5,
        color="#0066cc", label=player_name
    )

    ax.plot(
        group_filtered['year_since_debut'],
        group_filtered['rating_avg'],
        linestyle='--', linewidth=2,
        color="#ffa726", label=f"Grupo promedio: {pred_label}"
    )

    ax.plot(
        group_filtered['year_since_debut'],
        group_filtered['projection'],
        linestyle=':', linewidth=2,
        color="#2e7d32", label="Proyección ajustada"
    )

    ax.set_title(f"Evolución y proyección de {player_name}", fontsize=16, weight='bold')
    ax.set_xlabel("Años desde el debut", fontsize=12)
    ax.set_ylabel("Rating por 90 minutos", fontsize=12)
    ax.tick_params(axis='both', labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='lower center', fontsize=10)

    fig.tight_layout()
    print("🧪 Datos antes de graficar:")
    print(group_curve[['year_since_debut', 'rating_avg', 'projection']].head())

    return fig
