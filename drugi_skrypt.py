from urllib.parse import urljoin
import csv
import json
import requests
from bs4 import BeautifulSoup
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://www.otodom.pl"
JSON_FILE = "wyniki.json"

# Sprawdzenie, czy plik JSON istnieje, jeśli nie - tworzymy pusty plik
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w", encoding="utf-8") as jsonfile:
        json.dump([], jsonfile, indent=4, ensure_ascii=False)

# Lista do przechowywania ofert
oferty = []

with open("plik.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Pomijamy nagłówek

    for numer, link in reader:
        pełny_link = urljoin(BASE_URL, link)
        response = requests.get(pełny_link, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            opis = soup.find('div', attrs={"data-sentry-component": "AdHeaderBase"})

            if opis:
                cena = opis.find('div', attrs={"data-sentry-element": "MainPriceWrapper"})
                cenam2 = opis.find('div', attrs={"data-sentry-element": "AdditionalPriceWrapper"})
                miejscowosc = opis.find('div', attrs={"data-sentry-component": "MapLink"})
                description = opis.find('span', class_="css-ziqzm e1w2q53h5")
                parameters = opis.find_all('div', attrs={"data-sentry-element": "ItemGridContainer"})

                # Pobieramy tekst, jeśli element istnieje
                cena_text = cena.text.strip() if cena and cena.text else "Brak"
                cenam2_text = cenam2.text.strip() if cenam2 and cenam2.text else "Brak"
                miejscowosc_text = miejscowosc.text.strip() if miejscowosc and miejscowosc.text else "Brak"
                description_text = description.text.strip() if description and description.text else "Brak"

                # Tworzymy listę parametrów
                parameters_list = []
                if parameters:
                    for param in parameters:
                        name = param.find('span', class_="name")
                        value = param.find('span', class_="value")
                        if name and value:
                            parameters_list.append({"name": name.text.strip(), "value": value.text.strip()})

                # Tworzymy obiekt JSON dla oferty
                oferta = {
                    "price": cena_text,
                    "price_per_m2": cenam2_text,
                    "link_to_offer": pełny_link,
                    "district": miejscowosc_text,
                    "description": description_text,
                    "parameters": parameters_list
                }

                # Wyświetlamy dane przed zapisaniem do JSON-a
                print(f"\n🔹 Oferta {numer}:")
                print(json.dumps(oferta, indent=4, ensure_ascii=False))

                # Sprawdzamy, czy oferta faktycznie zawiera dane
                if oferta["price"] != "Brak" or oferta["description"] != "Brak":
                    oferty.append(oferta)
                    print(f"✅ Oferta {numer}: Dodano do listy ofert\n")
                else:
                    print(f"⚠ Oferta {numer}: Nie zawiera danych, pomijam!\n")

            else:
                print(f"❌ Oferta {numer}: Nie znaleziono opisu")
        else:
            print(f"⚠ Oferta {numer}: Błąd pobierania strony ({response.status_code})")

# **Zapisywanie do JSON tylko jeśli są dane**
if oferty:
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as jsonfile:
            json.dump(oferty, jsonfile, indent=4, ensure_ascii=False)
            jsonfile.flush()  # **Wymuszenie zapisu na dysk**
            print(f"\n✅ Wszystkie dane zostały zapisane do {JSON_FILE}")
    except Exception as e:
        print(f"\n❌ Błąd zapisu do pliku JSON: {e}")
else:
    print("\n⚠ Brak danych do zapisania w JSON!")