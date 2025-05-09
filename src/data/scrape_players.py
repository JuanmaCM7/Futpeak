#Lamine Yamal Scraper

import pandas as pd
import time
from pathlib import Path

# Set project root (script context)
project_root = Path(__file__).resolve().parents[1]
raw_data_path = project_root / "data" / "raw"
raw_data_path.mkdir(parents=True, exist_ok=True)

def scrape_lamine_yamal():
    """
    Scrapes match log data for Lamine Yamal across multiple seasons.
    Saves the result as a CSV in the raw data folder.
    """
    player_name = "lamine_yamal"
    player_id = "82ec26c1"
    seasons = ["2022-2023", "2023-2024", "2024-2025"]
    base_url = "https://fbref.com/en/players/{id}/matchlogs/{season}/{name}-Match-Logs"
    
    all_seasons_data = []

    for season in seasons:
        url = base_url.format(id=player_id, season=season, name=player_name.replace("_", "-").title())
        print(f"🌍 Scraping: {player_name} – {season}")

        try:
            df = pd.read_html(url, attrs={"id": "matchlogs_all"})[0]

            if df.columns.nlevels > 1:
                df.columns = df.columns.get_level_values(-1)

            df = df[df["Date"].notna()]
            df["Season"] = season
            all_seasons_data.append(df)

        except Exception as e:
            print(f"❌ Error scraping {season}: {e}")

        time.sleep(1)

    if all_seasons_data:
        df_lamine = pd.concat(all_seasons_data, ignore_index=True)
        file_path = raw_data_path / f"{player_name}_raw.csv"
        df_lamine.to_csv(file_path, index=False)
        print(f"✅ Data saved to: {file_path} with {len(df_lamine)} rows.")
    else:
        print("⚠️ No data was scraped.")

# Run the scraper when script is executed directly
if __name__ == "__main__":
    scrape_lamine_yamal()
