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

            price = soup.find("strong", attrs={"data-cy": "adPageHeaderPrice"})
            price_per_sqm = soup.find("div", attrs={"aria-label": "Cena za metr kwadratowy"})
            location = soup.find("a", attrs={"data-sentry-element": "StyledLink"})
            area = soup.find("div", attrs={"data-sentry-element": "ItemGridContainer"})

            next_data_script = soup.find("script", id="__NEXT_DATA__")
            description_text = "Nie znaleziono opisu"

            if next_data_script:
                try:
                    next_data_json = json.loads(next_data_script.string)
                    raw_description = next_data_json.get("props", {}).get("pageProps", {}).get("ad", {}).get("description", "Nie znaleziono opisu")
                    description_text = BeautifulSoup(raw_description, "html.parser").get_text(separator=" ", strip=True)
                except json.JSONDecodeError:
                    description_text = "❌ Błąd dekodowania JSON"

            price_text = price.text.strip() if price else "Nie dostępne"
            price_per_sqm_text = price_per_sqm.text.strip() if price_per_sqm else "Nie dostępne"
            location_text = location.text.strip() if location else "Nie dostępne"
            area_text = area.text.strip() if area else "Nie dostępne"

            with open("/app/config.yaml", "r") as api:
                config = yaml.safe_load(api)
            openai_api_key = config["api_key"]

            client = openai.OpenAI(api_key=openai_api_key)

            json_schema = {
                "name": "ranking",
                "description": "Ocena nieruchomości w skali od 1 do 10.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "integer",
                            "description": "Ocena nieruchomości w skali od 1 do 10."
                        }
                    },
                    "required": ["score"],
                    "additionalProperties": False
                }
            }

            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-nano",
                    messages=[
                        {"role": "system", "content": "Jesteś ekspertem od nieruchomości. Podaj ocenę mieszkania w skali 1–10 bez uzasadnienia."},
                        {"role": "user", "content": f"Oceń mieszkanie: {description_text}"}
                    ],
                    functions=[json_schema],
                    function_call="auto"
                )
                ai_opinion = response.choices[0].message.function_call.arguments
            except Exception as e:
                ai_opinion = f"❌ Błąd zapytania do OpenAI: {e}"

            offer = {
                "price": price_text,
                "price_per_m2": price_per_sqm_text,
                "link_to_offer": full_link,
                "district": location_text,
                "area": area_text,
                "description": description_text,
                "ai_rating": ai_opinion
            }

            print(f"Offer {number}")
            print(json.dumps(offer, indent=4, ensure_ascii=False))
            offers.append(offer)

        else:
            print(f"⚠ Offer {number}: Error fetching the page ({response.status_code})")

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