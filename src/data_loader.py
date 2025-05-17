# src/data_loader.py
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/processed")
IMG_DIR = Path("streamlit/assets/players")


def load_cleaned_matchlogs():
    return pd.read_csv(DATA_DIR / "cleaned_matchlogs.csv")


def load_future_matchlogs():
    return pd.read_csv(DATA_DIR / "future_stars_cleaned_matchlogs.csv")


def load_cleaned_metadata():
    return pd.read_csv(DATA_DIR / "cleaned_metadata.csv")


def load_future_metadata():
    return pd.read_csv(DATA_DIR / "future_stars_cleaned_metadata.csv")


def get_matchlogs_by_player(name, future=True):
    df = load_future_matchlogs() if future else load_cleaned_matchlogs()
    return df[df["Player_name"].str.lower() == name.lower()]


def get_metadata_by_player(name, future=True):
    df = load_future_metadata() if future else load_cleaned_metadata()
    return df[df["Player_name"].str.lower() == name.lower()].iloc[0].to_dict()

def get_name_id_mapping(future=True):
    df = load_future_metadata() if future else load_cleaned_metadata()
    return df[["Player_name", "Player_ID"]].dropna().drop_duplicates()

def get_player_image_path(player_name: str) -> Path | None:
    metadata = load_future_metadata()
    
    try:
        player_id = metadata.loc[metadata["Player_name"] == player_name, "Player_ID"].values[0]
    except IndexError:
        return None

    # Ruta absoluta desde raíz del proyecto
    img_path = Path(__file__).parents[1] / "assets" / "player_faces" / f"{player_id}.png"
    
    return img_path if img_path.exists() else None
