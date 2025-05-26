from urllib.parse import urljoin
import csv
import json
import requests
from bs4 import BeautifulSoup
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

base_url = "https://www.otodom.pl/"
JSON_FILE = "results1.json"

if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w", encoding="utf-8") as json_file:
        json.dump([], json_file, indent=4, ensure_ascii=False)

offers=[]

with open("plik1.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)

    for number, link in reader:
        full_link = urljoin(base_url, link)
        response = requests.get(full_link, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            description_selector1 = soup.find("div", attrs={"data-sentry-element": "Container"})
            description_selector2 = soup.find("div", attrs={"data-sentry-element": "StyledListContainer"})
            description_selector3 = soup.find("div", attrs={"data-sentry-component": "AdDescriptionBase"})

            if not description_selector1:
                print("🚫 Nie znaleziono selektora 1")
            elif not description_selector2:
                print("🚫 Nie znaleziono selektora 2")
            elif not description_selector3:
                print("🚫 Nie znaleziono selektora 3")
            else:
                price = description_selector1.find("strong", attrs={"data-cy": "adPageHeaderPrice"})
                price_per_sqm = description_selector1.find("div", attrs={"aria-label": "Cena za metr kwadratowy"})
                location = description_selector1.find("a", attrs={"data-sentry-element": "StyledLink"})
                area = description_selector2.find("div", attrs={"data-sentry-element": "ItemGridContainer"})
                ''' description = description_selector3.find_all("p")'''
                if description_selector3:
                    span_element = description_selector3.find("span")
                    if span_element:
                        first_paragraph = span_element.find("p")
                        description_text = first_paragraph.get_text(strip=True) if first_paragraph else "Nie dostępne"
                    else:
                        description_text = "Nie znaleziono span w sekcji opisu"
                else:
                    description_text = "Nie znaleziono div z opisem"
                    

                

                price_text = price.text.strip() if price else "Nie dostępne"
                price_per_sqm_text = price_per_sqm.text.strip() if price_per_sqm else "Nie dostępne"
                location_text = location.text.strip() if location else "Nie dostępne"
                area_text = area.text.strip() if area else "Nie dostępne"
                '''description_text = description[1].get_text(strip=True) if description else "Nie dostępne"'''


            

                offer = {
                    "price": price_text,
                    "price_per_m2": price_per_sqm_text,
                    "link_to_offer": full_link,
                    "district": location_text,
                    "area": area_text,
                    "descrption": description_text
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
            jsonfile.flush()  # **Wymuszenie zapisu na dysk**
            print(f"\n✅ All data has been saved to {JSON_FILE}")
    except Exception as e:
        print(f"\n❌ Error saving to JSON file: {e}")
else:
    print("\n⚠ No data available to save in JSON!")