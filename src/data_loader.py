from pathlib import Path
import pandas as pd
import requests
import streamlit as st

# === Directorios base ===
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "data" / "processed"
IMG_DIR = BASE_DIR / "assets" / "players_faces"

# === IDs de archivos en Google Drive ===
CSV_URLS = {
    "players": "1DfKmoc0KGWjg5yuGN4VsMgCqWTxLEUmT",
    "matches": "1BR4hUKb8op_cNC-wDz3c2x9mTY2taRLG",
    "future_players": "1_52Etuz7rGfKpbaWU5SqTazSwEd0pBsr",
    "future_matches": "1eFjerIs9g5v2XoLkEPigv6SI2QR7nRdf",
}

# === Función de descarga y carga ===
@st.cache_data
def download_csv_from_drive(file_id: str, output_path: Path) -> pd.DataFrame:
    if not output_path.exists():
        # ✅ Crear carpeta si no existe
        output_path.parent.mkdir(parents=True, exist_ok=True)

        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(url)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

    return pd.read_csv(output_path)

# === Funciones de carga ===
def load_cleaned_matchlogs() -> pd.DataFrame:
    return download_csv_from_drive(
        CSV_URLS["matches"],
        DATA_DIR / "cleaned_matchlogs.csv"
    )

def load_future_matchlogs() -> pd.DataFrame:
    return download_csv_from_drive(
        CSV_URLS["future_matches"],
        DATA_DIR / "future_stars_cleaned_matchlogs.csv"
    )

def load_cleaned_metadata() -> pd.DataFrame:
    return download_csv_from_drive(
        CSV_URLS["players"],
        DATA_DIR / "cleaned_metadata.csv"
    )

def load_future_metadata() -> pd.DataFrame:
    return download_csv_from_drive(
        CSV_URLS["future_players"],
        DATA_DIR / "future_stars_cleaned_metadata.csv"
    )

# === Funciones auxiliares ===
def get_matchlogs_by_player(player_id, future: bool = True) -> pd.DataFrame:
    df = load_future_matchlogs() if future else load_cleaned_matchlogs()
    return df[df["Player_ID"] == player_id]

def get_metadata_by_player(name: str, future: bool = True) -> dict:
    df = load_future_metadata() if future else load_cleaned_metadata()
    row = df[df["Player_name"].str.lower() == name.lower()]
    return row.iloc[0].to_dict() if not row.empty else {}

def get_name_id_mapping(metadata_df: pd.DataFrame) -> dict[str, str]:
    return dict(
        zip(
            metadata_df["Player_name"],
            metadata_df["Player_ID"].astype(str)
        )
    )

def get_player_image_path(player_name: str, metadata_df: pd.DataFrame) -> Path | None:
    mapping = get_name_id_mapping(metadata_df)
    player_id = mapping.get(player_name)
    if not player_id:
        return None

    img_file = IMG_DIR / f"{player_id}.png"
    return img_file if img_file.exists() else None
