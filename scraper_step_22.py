from urllib.parse import urljoin
import csv
import json
import requests
from bs4 import BeautifulSoup
import sys
import os
import yaml
import openai

sys.stdout.reconfigure(encoding="utf-8")

base_url = "https://www.otodom.pl/"
JSON_FILE = "results1.json"

if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w", encoding="utf-8") as json_file:
        json.dump([], json_file, indent=4, ensure_ascii=False)

offers = []

with open("/app/plik1.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)

    for number, link in reader:
        full_link = urljoin(base_url, link)
        response = requests.get(full_link, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Pobranie danych o cenie, lokalizacji itd.
            description_selector1 = soup.find("div", attrs={"data-sentry-element": "Container"})
            description_selector2 = soup.find("div", attrs={"data-sentry-element": "StyledListContainer"})
            description_selector3 = soup.find("div", attrs={"data-sentry-component": "AdDescriptionBase"})

            if not description_selector1 or not description_selector2 or not description_selector3:
                print(f"🚫 Brak jednego z selektorów dla oferty {number}")
                continue  # Jeśli któryś selektor nie istnieje, pomijamy ofertę

            price = description_selector1.find("strong", attrs={"data-cy": "adPageHeaderPrice"})
            price_per_sqm = description_selector1.find("div", attrs={"aria-label": "Cena za metr kwadratowy"})
            location = description_selector1.find("a", attrs={"data-sentry-element": "StyledLink"})
            area = description_selector2.find("div", attrs={"data-sentry-element": "ItemGridContainer"})

            # Pobranie opisu z `#__NEXT_DATA__`
            next_data_script = soup.find("script", id="__NEXT_DATA__")

            if next_data_script:
                try:
                    next_data_json = json.loads(next_data_script.string)
                    raw_description = next_data_json.get("props", {}).get("pageProps", {}).get("ad", {}).get(
                        "description", "Nie znaleziono opisu"
                    )
                    soup_description = BeautifulSoup(raw_description, "html.parser")
                    description_text = soup_description.get_text(separator=" ", strip=True)
                except json.JSONDecodeError:
                    description_text = "❌ Błąd dekodowania JSON"
            else:
                description_text = "❌ Nie znaleziono `#__NEXT_DATA__`"

            # Pobieranie wartości do JSON
            price_text = price.text.strip() if price else "Nie dostępne"
            price_per_sqm_text = price_per_sqm.text.strip() if price_per_sqm else "Nie dostępne"
            location_text = location.text.strip() if location else "Nie dostępne"
            area_text = area.text.strip() if area else "Nie dostępne"

            # Wczytaj klucz API
            with open("/app/config.yaml", "r") as api:
                config = yaml.safe_load(api)
            openai_api_key = config["api_key"]

            # Utwórz klienta OpenAI
            client = openai.OpenAI(api_key=openai_api_key)

            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-nano",
                    messages=[
                        {"role": "system", "content": "Jesteś ekspertem od nieruchomości. Oceń ofertę na podstawie opisu."},
                        {"role": "user", "content": f"Oceń mieszkanie na podstawie opisu: {description_text}. Podaj tylko ocene od 1 do 10."}
                    ]
                )
                ai_opinion = response.choices[0].message.content
            except Exception as e:
                ai_opinion = f"❌ Błąd zapytania do OpenAI: {e}"

            offer = {
                "price": price_text,
                "price_per_m2": price_per_sqm_text,
                "link_to_offer": full_link,
                "district": location_text,
                "area": area_text,
                "description": description_text,
                "ai": ai_opinion
            }

            print(f"Offer {number}")
            print(json.dumps(offer, indent=4, ensure_ascii=False))
            offers.append(offer)

        else:
            print(f"⚠ Offer {number}: Error fetching the page ({response.status_code})")

# Zapisanie danych do JSON
if offers:
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as jsonfile:
            json.dump(offers, jsonfile, indent=4, ensure_ascii=False)
            jsonfile.flush()
            print(f"\n✅ Wszystkie dane zapisane do {JSON_FILE}")
    except Exception as e:
        print(f"\n❌ Błąd zapisu do pliku JSON: {e}")
else:
    print("\n⚠ Brak danych do zapisania w JSON!")