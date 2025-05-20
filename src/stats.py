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

    #ax.set_title(f"G+A por año - {player_name}", fontsize=11, weight='bold')
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
    #ax.set_title(f"Minutos por año - {player_name}", fontsize=11, weight="bold")
    ax.set_xlabel("Año desde debut")
    ax.set_ylabel("Minutos jugados")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig

def plot_rating_projection(
    player_name: str,
    player_seasonal: pd.DataFrame,
    group_curve: pd.DataFrame,
    pred_label: str
) -> plt.Figure:
    """
    Evolución y proyección del rating por 90 minutos:
    - Línea sólida azul con puntos para el jugador.
    - Línea discontinua naranja para el grupo promedio.
    - Línea punteada verde para la proyección ajustada.
    Con fondo transparente y grid blanco sin marcos internos.
    """
    # 1) Preparar tema transparente
    sns.set_theme(style="whitegrid", rc={
        "axes.facecolor":   "none",
        "figure.facecolor": "none"
    })

    # 2) Cast de columna numérica
    player_seasonal = player_seasonal.copy()
    player_seasonal["year_since_debut"] = pd.to_numeric(
        player_seasonal["year_since_debut"], errors="coerce"
    )
    player_seasonal["rating_per_90"] = pd.to_numeric(
        player_seasonal["rating_per_90"], errors="coerce"
    )

    # 3) Filtrar rango razonable
    player_filtered = player_seasonal[player_seasonal["year_since_debut"] <= 13]
    group_filtered = group_curve.copy()
    group_filtered["year_since_debut"] = pd.to_numeric(
        group_filtered["year_since_debut"], errors="coerce"
    )

    # 4) Crear figura y eje transparentes
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="none")
    ax.set_facecolor("none")

    # 5) Quitar bordes (spines) internos
    for spine in ax.spines.values():
        spine.set_visible(False)

    # 6) Plot de las tres curvas
    # línea jugador
    ax.plot(
        player_filtered['year_since_debut'],
        player_filtered['rating_per_90'],
        marker='o', markersize=10, linewidth=3,
        color="#1f78b4", label=player_name  # un azul más vivo
    )

    # línea grupo
    ax.plot(
        group_filtered['year_since_debut'],
        group_filtered['rating_avg'],
        linestyle='--', linewidth=3,
        color="#e31a1c",               # pasa a rojo vivo
        label=f"Grupo promedio: {pred_label}"
    )

    # línea proyección
    ax.plot(
        group_filtered['year_since_debut'],
        group_filtered['projection'],
        linestyle=':', linewidth=3,
        color="#33a02c",               # un verde fuerte
        label="Proyección ajustada"
    )

    # 7) Grid blanco y estilo de ticks
    ax.grid(True, color="white", linestyle="--", alpha=0.4)
    #ax.grid(False) # Quitar grid si queremos
    ax.tick_params(colors="white", labelsize=10)
    

    # 8) Etiquetas en dorado con cuadro de fondo
    # Etiquetas con un poco de separación
    ax.set_xlabel(
        "Años desde el debut", 
        fontsize=12, 
        color="#ffd700",
        labelpad=12     # <- espacio extra abajo
    )
    ax.set_ylabel(
        "Rating por 90 minutos", 
        fontsize=12, 
        color="#ffd700",
        labelpad=12     # <- espacio extra a la izquierda
    )

    # Separar también los números de los ticks
    ax.tick_params(
        axis="x",
        colors="white",
        labelsize=10,
        pad=6          # <- sube o baja este valor según necesidad
    )

    # 9) Poner un recuadro suave detrás de las etiquetas
    xlabel = ax.xaxis.label
    xlabel.set_bbox({
        "facecolor": "black",
        "alpha": 0.3,
        "edgecolor": "white",
        "boxstyle": "round,pad=0.3"
    })
    ylabel = ax.yaxis.label
    ylabel.set_bbox({
        "facecolor": "black",
        "alpha": 0.3,
        "edgecolor": "white",
        "boxstyle": "round,pad=0.3"
    })

    # 10) Leyenda con marco
    leg = ax.legend(loc="lower center", fontsize=10, frameon=True)

    # 11) Texto en blanco
    for txt in leg.get_texts():
        txt.set_color("white")

    # 12) Sombreado sutil detrás de la leyenda
    frame = leg.get_frame()
    frame.set_facecolor("black")   # fondo negro
    frame.set_alpha(0.3)           # 30% de opacidad
    frame.set_edgecolor("white")   # borde blanco suave
    frame.set_linewidth(0.5)       # grosor de borde

    fig.tight_layout()
    return fig

