# FUTPEAK - Proyecto de Scraping y Predicción de Carreras de Futbolistas

## Descripción
Scraping de datos de jugadores, partidos y competiciones de fútbol profesional para el análisis de trayectorias deportivas.

## Estructura del Proyecto
- data/meta/
  - male_players.yaml
  - male_players_metadata.csv
  - male_competitions.csv
- notebooks/
  - tests.ipynb (desarrollo de scraping)
- scripts/ (pendiente de organizar)

## Cómo empezar
1. Clonar el repositorio.
2. Crear el entorno conda:

conda env create -f environment.yml

3. Activar el entorno:

conda activate futpeak

4. Ejecutar los notebooks o scripts.

## Dependencias
- Python 3.10
- Selenium
- BeautifulSoup4
- pandas
- PyYAML
- tqdm (opcional)

## Estado
🚧 Proyecto en desarrollo. Actualmente completando scraping de metadata de jugadores.


# Obtención de metadata:
```
# Metadata players

# 📦 Imports
import yaml
import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from pathlib import Path
import random

# === Paths ===
YAML_PATH = "data/meta/male_players.yaml"
OUTPUT_FILE = Path("data/meta/male_players_metadata.csv")
CHROME_PATH = "C:/Windows/System32/chromedriver.exe"

# === Load YAML
with open(YAML_PATH, "r", encoding="utf-8") as f:
    players = yaml.safe_load(f)

# === Set the last scraped URL (for continuation)
# Leave it empty "" to scrape from the beginning
last_scraped_url = ""

# === Find starting point
start_index = 0  # By default start from 0

if last_scraped_url:
    for idx, player in enumerate(players):
        if player["url_template"] == last_scraped_url:
            start_index = idx + 1  # Start AFTER the last scraped player
            break
    else:
        raise ValueError("❌ last_scraped_url not found in male_players.yaml!")

players = players[start_index:]  # Only keep players after last scraped

print(f"🚀 Starting scraping from index {start_index} ({players[0]['name']})")

# === Setup Selenium
options = Options()
# options.add_argument("--headless")  # Optional: hide browser if you want
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
service = Service(executable_path=CHROME_PATH)
driver = webdriver.Chrome(service=service, options=options)

# === Metadata extraction
def extract_metadata(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    meta = soup.find("div", id="meta")
    if not meta:
        return {}

    try:
        full_name = meta.find("p").text.strip()
    except:
        full_name = None

    position = footed = None
    try:
        pos_block = meta.find("strong", string="Position:").parent
        if pos_block:
            text = pos_block.get_text(separator="|")
            parts = text.split("|")
            position = parts[1].strip() if len(parts) > 1 else None
            footed = parts[3].strip() if "Footed:" in text and len(parts) > 3 else None
    except:
        pass

    birth_date = age = birth_place = None
    try:
        birth_tag = meta.find("strong", string="Born:")
        if birth_tag:
            birth_block = birth_tag.parent
            date_span = birth_block.find("span")
            if date_span:
                birth_date = date_span.get("data-birth")
                if not birth_date:
                    raw_text = date_span.text.strip()
                    try:
                        birth_date = pd.to_datetime(raw_text).strftime("%Y-%m-%d")
                    except:
                        birth_date = None

            nobr = birth_block.find("nobr")
            if nobr:
                raw_age = nobr.text
                match = re.search(r"Age:\s*([\d\-]+)", raw_age)
                age = match.group(1) if match else None

            birth_place_span = nobr.find_next("span") if nobr else None
            if birth_place_span:
                birth_place = birth_place_span.text.strip()
    except:
        pass

    nationality = None
    try:
        nat_tag = meta.find("strong", string="National Team:")
        if nat_tag:
            nationality = nat_tag.find_next("a").text.strip()
    except:
        pass

    if not nationality:
        try:
            citizen_tag = meta.find("strong", string="Citizenship:")
            if citizen_tag:
                nationality = citizen_tag.find_next("a").text.strip()
        except:
            pass

    club = None
    try:
        club_tag = meta.find("strong", string="Club:")
        if club_tag:
            club = club_tag.find_next("a").text.strip()
    except:
        pass

    return {
        "full_name": full_name,
        "position": position,
        "footed": footed,
        "birth_date": birth_date,
        "age": age,
        "birth_place": birth_place,
        "nationality": nationality,
        "club": club
    }

# === Create output file if not exists
if not OUTPUT_FILE.exists():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=[
        "player_name", "url_template", "full_name", "position", "footed",
        "birth_date", "age", "birth_place", "nationality", "club"
    ]).to_csv(OUTPUT_FILE, index=False)

# === Main loop
for i, player in enumerate(players, start=start_index + 1):
    player_name = player["name"]
    player_url = player["url_template"]

    print(f"\n🔍 [{i}] Scraping: {player_url}")

    retries = 0
    max_retries = 3
    success = False

    while retries < max_retries and not success:
        try:
            driver.get(player_url)
            sleep_time = random.uniform(8, 12)
            print(f"⏳ Waiting {sleep_time:.2f} seconds after loading...")
            time.sleep(sleep_time)

            data = extract_metadata(driver)
            if not data:
                print(f"⚠️ No metadata found for {player_name}")
                break

            data["player_name"] = player_name
            data["url_template"] = player_url

            pd.DataFrame([data]).to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
            print(f"✅ Saved metadata for {player_name}")
            success = True

        except WebDriverException as e:
            if "ERR_INTERNET_DISCONNECTED" in str(e):
                retries += 1
                print(f"⚠️ Internet disconnected. Retrying ({retries}/{max_retries})...")
                time.sleep(10)
            else:
                print(f"❌ WebDriver error: {e}")
                break

driver.quit()
print(f"\n💾 Done! Full metadata saved to: {OUTPUT_FILE}")
```