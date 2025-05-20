import pandas as pd
from player_processing import build_player_df, calculate_rating_per_90, build_annual_profile
from model_utils import load_model_assets

# Cargar modelos y componentes
model, le, df_curves, model_features = load_model_assets()

# -------------------------
# Preparar input del jugador para el modelo
# -------------------------

def prepare_features(player_id: str):
    df = build_player_df(player_id)

    print(f"\n🧪 HEAD desde Streamlit para {player_id}:")
    print(df[["Date", "Minutes", "Goals", "Assists", "Age"]].head())

    # Asegúrate Date es datetime (build_player_df ya lo hace, pero por si acaso):
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Calcula rating_por_90
    df = calculate_rating_per_90(df)

    player_model_df, seasonal_df = build_annual_profile(df)

    # Asegúrate de que es UNA SOLA FILA
    if player_model_df.shape[0] != 1:
        raise ValueError(f"❌ Error: el perfil vectorizado tiene {player_model_df.shape[0]} filas. Esperada 1.")

    X_input = (
        player_model_df
        .reindex(columns=model_features, fill_value=0)
        .mean(axis=0)
        .to_frame()
        .T
        .reindex(columns=model_features, fill_value=0)
    )


    print(f"🧠 Vector model input para {player_id} (Streamlit):")
    print(player_model_df.T)

    return X_input, seasonal_df


# -------------------------
# Predecir grupo de evolución
# -------------------------
def predict_peak_group(df_model: pd.DataFrame) -> str:
    pred = model.predict(df_model)[0]
    return le.inverse_transform([pred])[0]

# -------------------------
# Función modularizada para predecir grupo (desde notebook o app)
# -------------------------

def predict_player_group(model, label_encoder, model_columns, player_model_df, player_id):
    print(f"🧠 ID actual: {player_id}")
    print(f"🎯 Datos pasados al modelo:\n{X_input.T}")
    X_input = player_model_df.reindex(columns=model_columns, fill_value=0)
    pred_encoded = model.predict(X_input)[0]
    return label_encoder.inverse_transform([pred_encoded])[0]

# -------------------------
# Obtener curva del grupo predicho
# -------------------------
def get_curve_by_group(group: str) -> pd.DataFrame:
    print("🧪 Buscando grupo:", group)
    print("📊 Valores únicos en df_curves:", df_curves['peak_group'].unique())
    return df_curves[df_curves['peak_group'] == group].copy()


# -------------------------
# Ajustar la proyección de la curva del grupo
# -------------------------
def adjust_projection(group_curve: pd.DataFrame, player_seasonal: pd.DataFrame) -> pd.DataFrame:
    try:
        last_real_year = player_seasonal['year_since_debut'].max()
        last_real_rating = player_seasonal.loc[player_seasonal['year_since_debut'] == last_real_year, 'rating_per_90'].values[0]
        ref_value = group_curve.loc[group_curve['year_since_debut'] == last_real_year, 'rating_avg'].values[0]
        shift = last_real_rating - ref_value
        group_curve['projection'] = group_curve['rating_avg'] + shift
    except Exception as e:
        print(f"❌ No se pudo ajustar la proyección: {e}")
        group_curve['projection'] = group_curve['rating_avg']
    return group_curve


# -------------------------
# Predicción completa + ajuste de curva
# -------------------------
def predict_and_project_player(player_id: str):
    from data_loader import load_future_metadata

    metadata = load_future_metadata()
    player_name = metadata[metadata['Player_ID'] == player_id]['Player_name'].values[0]
    df_model, seasonal = prepare_features(player_id)
    print("🧪 INPUT final que se envía al modelo:")
    print(df_model.T)

    group = predict_peak_group(df_model)
    curve = get_curve_by_group(group)

    # Ajustar proyección
    try:
        curve = adjust_projection(curve, seasonal)
    except Exception as e:
        print(f"❌ Error en proyección de {player_name}: {e}")
        curve['projection'] = curve['rating_avg']

    # Asegurar formato correcto
    seasonal['year_since_debut'] = pd.to_numeric(seasonal['year_since_debut'], errors='coerce').fillna(0).astype(int)
    curve['year_since_debut'] = pd.to_numeric(curve['year_since_debut'], errors='coerce').fillna(0).astype(int)

    seasonal = seasonal[seasonal['year_since_debut'] <= 13]
    curve = curve[curve['year_since_debut'] <= 13]
    print("🧾 projection types:", curve['projection'].apply(type).unique())
    print("✅ projection nulls:", curve['projection'].isna().sum())
    if 'projection' not in curve.columns:
        print("⚠️ projection no generada. Reintentando.")
        curve = adjust_projection(curve, seasonal)

    return group, seasonal, curve
