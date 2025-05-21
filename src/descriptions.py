def generar_conclusion(player_id: str) -> str:
    from model_runner import predict_and_project_player
    from data_loader import load_future_metadata
    from player_processing import build_player_df
    import pandas as pd

    group_label, seasonal_df, group_curve = predict_and_project_player(player_id)
    metadata = load_future_metadata()
    player_row = metadata[metadata["Player_ID"] == player_id]
    player_name = player_row["Player_name"].values[0]

    # Año natural de debut desde matchlogs
    matchlogs = build_player_df(player_id)
    matchlogs = matchlogs[matchlogs["Minutes"] > 0].sort_values("Date")
    debut_natural_year = pd.to_datetime(matchlogs.iloc[0]["Date"]).year

    # Orden y limpieza de seasonal
    seasonal_df = seasonal_df.sort_values("year_since_debut")
    seasonal_df["rating_per_90"] = pd.to_numeric(seasonal_df["rating_per_90"], errors="coerce")
    seasonal_df["Minutes"] = pd.to_numeric(seasonal_df["Minutes"], errors="coerce")
    seasonal_df["Goals"] = pd.to_numeric(seasonal_df.get("Goals", 0), errors="coerce")
    seasonal_df["Assists"] = pd.to_numeric(seasonal_df.get("Assists", 0), errors="coerce")
    seasonal_df["G+A"] = seasonal_df["Goals"] + seasonal_df["Assists"]

    # Debut row
    debut_row = seasonal_df[seasonal_df["year_since_debut"] == 1].iloc[0]
    debut_rating = debut_row["rating_per_90"]

    # Peak de rating
    peak_row = seasonal_df.loc[seasonal_df["rating_per_90"].idxmax()]
    peak_year_natural = debut_natural_year + (int(peak_row["year_since_debut"]) - 1)
    peak_rating = peak_row["rating_per_90"]

    # Bajón
    drop_row = seasonal_df.loc[seasonal_df["rating_per_90"].idxmin()]
    drop_year_natural = debut_natural_year + (int(drop_row["year_since_debut"]) - 1)
    drop_rating = drop_row["rating_per_90"]

    # Peak de producción ofensiva (G+A)
    peak_prod_row = seasonal_df.loc[seasonal_df["G+A"].idxmax()]
    peak_prod_year = debut_natural_year + (int(peak_prod_row["year_since_debut"]) - 1)
    peak_prod_value = int(peak_prod_row["G+A"])
    peak_prod_minutes = int(peak_prod_row["Minutes"])
    peak_prod_rating = peak_prod_row["rating_per_90"]

    # Último año disponible
    last_year_relative = int(seasonal_df["year_since_debut"].max())
    current_year = debut_natural_year + (last_year_relative - 1)

    # Narrativa
    conclusion = (
        f"{player_name} debutó en {debut_natural_year} con un rendimiento sorprendentemente alto "
        f"(rating de {debut_rating:.1f}), destacando por su eficacia en pocos minutos. "
    )

    if int(drop_row["year_since_debut"]) > 1:
        conclusion += (
            f"En {drop_year_natural}, su rendimiento cayó hasta {drop_rating:.1f}, coincidiendo con un aumento "
            "en su carga de minutos y un posible proceso de adaptación."
        )

    conclusion += (
        f" En {peak_prod_year}, alcanzó su año de máxima producción ofensiva, con {peak_prod_value} goles + asistencias, "
        f"{peak_prod_minutes} minutos acumulados y un rating sostenido de {peak_prod_rating:.1f}. "
    )

    if peak_row["year_since_debut"] != peak_prod_row["year_since_debut"]:
        conclusion += (
            f"Sin embargo, su mejor rendimiento específico se registró en {peak_year_natural} "
            f"({peak_rating:.1f})."
        )

    conclusion += (
        " Su curva refleja una evolución coherente, con un proceso de aprendizaje temprano seguido de consolidación. "
        "Según nuestro modelo, es un perfil con alta proyección si mantiene este ritmo competitivo."
    )

    return conclusion