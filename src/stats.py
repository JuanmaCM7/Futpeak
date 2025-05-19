import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from data_loader import get_matchlogs_by_player, get_metadata_by_player
from player_processing import build_player_df, aggregate_stats_by_year

def get_player_stats(player_id):
    df = get_matchlogs_by_player(player_id=player_id, future=True).copy()

    df['Goals']   = pd.to_numeric(df['Goals'], errors='coerce')
    df['Assists'] = pd.to_numeric(df['Assists'], errors='coerce')
    df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce')
    df['Date']    = pd.to_datetime(df['Date'], errors='coerce')

    if df.empty:
        return pd.DataFrame()

    df['Natural_year'] = df['Date'].dt.year
    debut_year = df[df['Minutes'] > 0]['Natural_year'].min()
    df['year_since_debut'] = df['Natural_year'] - debut_year + 1

    stats = (
        df.groupby('year_since_debut')
          .agg({
              'Goals': 'sum',
              'Assists': 'sum',
              'Minutes': 'sum',
              'Date': 'count'
          })
          .rename(columns={'Date': 'Matches'})
          .reset_index()
    )
    stats['G+A'] = stats['Goals'] + stats['Assists']
    return stats


def plot_player_stats(player_id) -> plt.Figure:
    """Bar chart de Goles + Asistencias por año desde el debut."""
    stats = get_player_stats(player_id)
    player_name = get_metadata_by_player(player_id, future=True).get("Player_name", player_id)
    if stats.empty:
        return None

    # transparent theme
    sns.set_theme(style="whitegrid", rc={
        "axes.facecolor":   "none",
        "figure.facecolor": "none"
    })
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="none")
    ax.set_facecolor("none")

    # remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # plot barras
    sns.barplot(
        data=stats,
        x='year_since_debut',
        y='G+A',
        color="#42a5f5",
        ax=ax
    )

    # grid blanco atenuado
    ax.grid(True, color="white", linestyle="--", alpha=0.2)

    # ejes dorados con separación
    ax.set_xlabel("Año desde debut", fontsize=12, color="#ffd700", labelpad=12)
    ax.set_ylabel("Goles + Asistencias", fontsize=12, color="#ffd700", labelpad=12)

    # ticks en blanco y separados
    ax.tick_params(axis="x", colors="white", labelsize=10, pad=6)
    ax.tick_params(axis="y", colors="white", labelsize=10, pad=6)

    # recuadro detrás de las etiquetas
    ax.xaxis.label.set_bbox({
        "facecolor": "black", "alpha": 0.3,
        "edgecolor": "white", "boxstyle": "round,pad=0.3"
    })
    ax.yaxis.label.set_bbox({
        "facecolor": "black", "alpha": 0.3,
        "edgecolor": "white", "boxstyle": "round,pad=0.3"
    })

    fig.tight_layout()
    return fig


def plot_minutes_per_year(player_id) -> plt.Figure:
    """Bar chart de Minutos totales por año desde el debut."""
    df = build_player_df(player_id)
    stats_df = aggregate_stats_by_year(df)
    if stats_df.empty:
        return None

    # transparent theme
    sns.set_theme(style="whitegrid", rc={
        "axes.facecolor":   "none",
        "figure.facecolor": "none"
    })
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="none")
    ax.set_facecolor("none")

    # remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # plot barras
    sns.barplot(
        data=stats_df,
        x="year_since_debut",
        y="Minutes",
        color="#66bb6a",
        ax=ax
    )

    # grid blanco atenuado
    ax.grid(True, color="white", linestyle="--", alpha=0.2)

    # ejes dorados con separación
    ax.set_xlabel("Año desde debut", fontsize=12, color="#ffd700", labelpad=12)
    ax.set_ylabel("Minutos jugados", fontsize=12, color="#ffd700", labelpad=12)

    # ticks en blanco y separados
    ax.tick_params(axis="x", colors="white", labelsize=10, pad=6)
    ax.tick_params(axis="y", colors="white", labelsize=10, pad=6)

    # recuadro detrás de las etiquetas
    ax.xaxis.label.set_bbox({
        "facecolor": "black", "alpha": 0.3,
        "edgecolor": "white", "boxstyle": "round,pad=0.3"
    })
    ax.yaxis.label.set_bbox({
        "facecolor": "black", "alpha": 0.3,
        "edgecolor": "white", "boxstyle": "round,pad=0.3"
    })

    fig.tight_layout()
    return fig


def plot_rating_projection(
    player_name: str,
    player_seasonal: pd.DataFrame,
    group_curve: pd.DataFrame,
    pred_label: str
) -> plt.Figure:
    """
    Evolución y proyección del rating por 90:
    Líneas definidas, fondo transparente, grid blanco suave,
    ejes y leyenda con estilo.
    """
    # tema transparente
    sns.set_theme(style="whitegrid", rc={
        "axes.facecolor":   "none",
        "figure.facecolor": "none"
    })

    # preparar datos
    df = player_seasonal.copy()
    df["year_since_debut"] = pd.to_numeric(df["year_since_debut"], errors="coerce")
    df["rating_per_90"]   = pd.to_numeric(df["rating_per_90"], errors="coerce")
    player_filtered = df[df["year_since_debut"] <= 13]

    gc = group_curve.copy()
    gc["year_since_debut"] = pd.to_numeric(gc["year_since_debut"], errors="coerce")

    # figura transparente
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="none")
    ax.set_facecolor("none")

    # quitar spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # trazar curvas
    ax.plot(
        player_filtered["year_since_debut"],
        player_filtered["rating_per_90"],
        marker="o", linestyle="-",
        color="#1f78b4", linewidth=3,
        label=player_name
    )
    if "rating_avg" in gc:
        ax.plot(
            gc["year_since_debut"],
            gc["rating_avg"],
            linestyle="--", color="#e31a1c", linewidth=3,
            label=f"Grupo promedio: {pred_label}"
        )
    if "projection" in gc:
        ax.plot(
            gc["year_since_debut"],
            gc["projection"],
            linestyle=":", color="#33a02c", linewidth=3,
            label="Proyección ajustada"
        )

    # grid suave
    ax.grid(True, color="white", linestyle="--", alpha=0.4)

    # ejes dorados con separación
    ax.set_xlabel("Años desde el debut", fontsize=12, color="#ffd700", labelpad=12)
    ax.set_ylabel("Rating por 90 minutos", fontsize=12, color="#ffd700", labelpad=12)

    ax.tick_params(axis="x", colors="white", labelsize=10, pad=6)
    ax.tick_params(axis="y", colors="white", labelsize=10, pad=6)

    # recuadros en etiquetas
    ax.xaxis.label.set_bbox({
        "facecolor": "black", "alpha": 0.3,
        "edgecolor": "white", "boxstyle": "round,pad=0.3"
    })
    ax.yaxis.label.set_bbox({
        "facecolor": "black", "alpha": 0.3,
        "edgecolor": "white", "boxstyle": "round,pad=0.3"
    })

    # leyenda con fondo sutil
    leg = ax.legend(loc="lower center", fontsize=10, frameon=True)
    for txt in leg.get_texts():
        txt.set_color("white")
    lf = leg.get_frame()
    lf.set_facecolor("black")
    lf.set_alpha(0.3)
    lf.set_edgecolor("white")
    lf.set_linewidth(0.5)

    fig.tight_layout()
    return fig
