# model_runner.py
import pandas as pd
import joblib
from data_loader import load_future_metadata, load_future_matchlogs

# Cargar objetos
model = joblib.load('model/futpeak_model_multi.joblib')
le = joblib.load('model/label_encoder.joblib')
df_curves = joblib.load('model/curvas_promedio.joblib')
model_features = joblib.load('model/model_features.joblib')

# -------------------------
# Función para preparar features del jugador
# -------------------------
def prepare_features(player_id: str) -> tuple:
    future_logs = load_future_matchlogs()
    future_meta = load_future_metadata()

    player_logs = future_logs[future_logs['Player_ID'] == player_id].copy()
    player_meta = future_meta[future_meta['Player_ID'] == player_id].copy()

    if player_logs.empty or player_meta.empty:
        raise ValueError("Datos del jugador no encontrados.")

    player_logs['Date'] = pd.to_datetime(player_logs['Date'], errors='coerce')
    player_meta['Birth_date'] = pd.to_datetime(player_meta['Birth_date'], errors='coerce')
    player_logs = player_logs.merge(player_meta[['Player_ID', 'Birth_date']], on='Player_ID', how='left')
    player_logs['Age'] = (player_logs['Date'] - player_logs['Birth_date']).dt.days / 365.25

    # Calcular rating_per_90
    def calculate_rating(row):
        score = (
            row['Goals'] * 5 +
            row['Assists'] * 4 +
            row['Shots_on_target'] * 0.5 +
            (row['Shots'] - row['Shots_on_target']) * 0.1 -
            row['Yellow_cards'] * 1 -
            row['Red_cards'] * 2
        )
        return score / (row['Minutes'] / 90) if row['Minutes'] > 0 else 0

    rating_cols = ['Goals', 'Assists', 'Shots', 'Shots_on_target', 'Yellow_cards', 'Red_cards', 'Minutes']
    for col in rating_cols:
        player_logs[col] = pd.to_numeric(player_logs[col], errors='coerce').fillna(0)
    player_logs['rating_per_90'] = player_logs.apply(calculate_rating, axis=1)

    player_logs = player_logs[player_logs['Minutes'] >= 70].copy()
    player_logs['Natural_year'] = player_logs['Date'].dt.year
    debut_year = player_logs[player_logs['Minutes'] > 0]['Natural_year'].min()
    player_logs['year_since_debut'] = player_logs['Natural_year'] - debut_year + 1

    seasonal = player_logs.groupby('year_since_debut').agg({
        'rating_per_90': 'mean',
        'Age': 'mean',
        'Minutes': 'sum'
    }).reset_index()

    pivot_rating = seasonal.pivot(columns='year_since_debut', values='rating_per_90')
    pivot_age = seasonal.pivot(columns='year_since_debut', values='Age')
    pivot_minutes = seasonal.pivot(columns='year_since_debut', values='Minutes')

    pivot_rating.columns = [f'rating_year_{i}' for i in pivot_rating.columns]
    pivot_age.columns = [f'age_year_{i}' for i in pivot_age.columns]
    pivot_minutes.columns = [f'minutes_year_{i}' for i in pivot_minutes.columns]

    df_model = pd.concat([pivot_rating, pivot_age, pivot_minutes], axis=1)
    if 'rating_year_2' in df_model and 'rating_year_1' in df_model:
        df_model['growth_2_1'] = df_model['rating_year_2'] - df_model['rating_year_1']
    if 'rating_year_3' in df_model and 'rating_year_2' in df_model:
        df_model['growth_3_2'] = df_model['rating_year_3'] - df_model['rating_year_2']
    df_model['avg_rating'] = df_model[[col for col in df_model.columns if 'rating_year_' in col]].mean(axis=1)
    df_model['sum_minutes'] = df_model[[col for col in df_model.columns if 'minutes_year_' in col]].sum(axis=1)
    if 'rating_year_3' in df_model and 'rating_year_1' in df_model:
        df_model['rating_trend'] = df_model['rating_year_3'] - df_model['rating_year_1']
    if 'minutes_year_3' in df_model and 'minutes_year_1' in df_model:
        df_model['minutes_trend'] = df_model['minutes_year_3'] - df_model['minutes_year_1']

    df_model = df_model.reindex(columns=model_features, fill_value=0)
    return df_model, seasonal

# -------------------------
# Función para predecir clase
# -------------------------
def predict_peak_group(df_model: pd.DataFrame) -> str:
    pred = model.predict(df_model)[0]
    return le.inverse_transform([pred])[0]

# -------------------------
# Función para obtener curva promedio del grupo
# -------------------------
def get_curve_by_group(group: str) -> pd.DataFrame:
    return df_curves[df_curves['peak_group'] == group].copy()

# -------------------------
# Función para preparar predicción y ajustar curva
# -------------------------
def predict_and_project_player(player_name: str):
    metadata = load_future_metadata()
    player_id = metadata[metadata['Player_name'] == player_name]['Player_ID'].values[0]
    df_model, seasonal = prepare_features(player_id)
    group = predict_peak_group(df_model)
    curve = get_curve_by_group(group)

    # Proyección ajustada
    try:
        last_year = seasonal['year_since_debut'].astype(int).max()
        last_rating = seasonal.loc[seasonal['year_since_debut'] == last_year, 'rating_per_90'].values[0]
        ref = curve.loc[curve['year_since_debut'] == last_year, 'rating_avg'].values[0]
        curve['projection'] = curve['rating_avg'] + (last_rating - ref)
    except Exception as e:
        print(f"❌ Error en proyección de {player_name}: {e}")
        curve['projection'] = curve['rating_avg']

    # ✅ Forzar tipo y filtrar correctamente
    seasonal['year_since_debut'] = pd.to_numeric(seasonal['year_since_debut'], errors='coerce').fillna(0).astype(int)
    curve['year_since_debut'] = pd.to_numeric(curve['year_since_debut'], errors='coerce').fillna(0).astype(int)

    seasonal = seasonal[seasonal['year_since_debut'] <= 13]
    curve = curve[curve['year_since_debut'] <= 13]

    return group, seasonal, curve
