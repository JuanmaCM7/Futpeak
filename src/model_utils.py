# model_utils.py

from pathlib import Path
import joblib
import streamlit as st

@st.cache_resource
def load_model_assets(model_dir: Path = Path(__file__).parents[1] / "model"):
    """
    Carga el modelo de clasificación, label encoder, curvas promedio y columnas del modelo.
    Retorna una tupla con (modelo, label encoder, curvas, columnas).
    """
    model = joblib.load(model_dir / "futpeak_model_multi.joblib")
    le = joblib.load(model_dir / "label_encoder.joblib")
    df_curves = joblib.load(model_dir / "curvas_promedio.joblib")
    model_features = joblib.load(model_dir / "model_features.joblib")
    return model, le, df_curves, model_features
