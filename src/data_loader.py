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


def get_player_image_path(name):
    filename = name.lower().replace(" ", "_") + ".png"
    path = IMG_DIR / filename
    return str(path) if path.exists() else None