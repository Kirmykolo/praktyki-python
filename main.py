from bs4 import BeautifulSoup
from requests import get
import sys
import csv
import json

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.bannerstop.com/produkte/banner-drucken/pvc-banner.html"

lista = []  

page = get(url)
produkty = BeautifulSoup(page.content, 'html.parser')


for produkt in produkty.find_all('div', class_='product-item-info'):
    nazwa = produkt.find('a', class_='product-item-link')
    sam_link = produkt.find('a', class_='product photo product-item-photo')

    if nazwa and sam_link:
        lista.append({
            "nazwa_produktu": nazwa.get_text(strip=True),
            "link": sam_link.get('href')
        })


for produkt in lista:
    print(f"Nazwa: {produkt['nazwa_produktu']}\nLink do produktu: {produkt['link']}\n")


with open("data.csv", mode="w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["nazwa_produktu", "link"])  # Dopasowane do kluczy w lista
    writer.writeheader()
    writer.writerows(lista)


with open("data.json", mode="w", encoding="utf-8") as file:
    json.dump(lista, file, indent=4, ensure_ascii=False)

