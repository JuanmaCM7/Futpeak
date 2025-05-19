from pathlib import Path
import pandas as pd

# Directorios base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "data" / "processed"
IMG_DIR  = BASE_DIR / "assets" / "players_faces"


def load_cleaned_matchlogs() -> pd.DataFrame:
    """Carga los registros de partidos limpiados."""
    return pd.read_csv(DATA_DIR / "cleaned_matchlogs.csv")


def load_future_matchlogs() -> pd.DataFrame:
    """Carga los registros de partidos de futuros talentos."""
    return pd.read_csv(DATA_DIR / "future_stars_cleaned_matchlogs.csv")


def load_cleaned_metadata() -> pd.DataFrame:
    """Carga la metadata limpia de todos los jugadores."""
    return pd.read_csv(DATA_DIR / "cleaned_metadata.csv")


def load_future_metadata() -> pd.DataFrame:
    """Carga la metadata de futuros talentos."""
    return pd.read_csv(DATA_DIR / "future_stars_cleaned_metadata.csv")


def get_matchlogs_by_player(player_id, future: bool = True) -> pd.DataFrame:
    """
    Devuelve los registros de partido de un jugador según su ID,
    sin forzar conversión a int.
    """
    df = load_future_matchlogs() if future else load_cleaned_matchlogs()
    return df[df["Player_ID"] == player_id]


def get_metadata_by_player(name: str, future: bool = True) -> dict:
    """
    Devuelve la fila de metadata de un jugador por nombre (no sensible a mayúsculas).
    """
    df = load_future_metadata() if future else load_cleaned_metadata()
    row = df[df["Player_name"].str.lower() == name.lower()]
    return row.iloc[0].to_dict() if not row.empty else {}


def get_name_id_mapping(metadata_df: pd.DataFrame) -> dict[str, str]:
    """
    Mapea cada nombre único de jugador a su Player_ID (en str),
    útil si lo necesitas en otro lugar.
    """
    return dict(
        zip(
            metadata_df["Player_name"],
            metadata_df["Player_ID"].astype(str)
        )
    )


def get_player_image_path(player_name: str, metadata_df: pd.DataFrame) -> Path | None:
    """
    Devuelve la ruta al PNG del jugador, nombrado con su Player_ID,
    o None si no existe.
    """
    mapping = get_name_id_mapping(metadata_df)
    player_id = mapping.get(player_name)
    if not player_id:
        return None

    img_file = IMG_DIR / f"{player_id}.png"
    return img_file if img_file.exists() else None
