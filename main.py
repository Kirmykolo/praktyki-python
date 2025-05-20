from bs4 import BeautifulSoup
from requests import get
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.bannerstop.com/produkte/banner-drucken/pvc-banner.html"

lista = []

page =get(url)

produkty = BeautifulSoup(page.content, 'html.parser')


for produkt in produkty.find_all('div', class_='product-item-info'):
    nazwa= produkt.find('a', 'product-item-link').get_text().strip()
    sam_link=produkt.find('a', 'product photo product-item-photo').get('href')


    
    if nazwa and sam_link:
       lista.append({
           "nazwa_produktu": nazwa,
           "link": sam_link
       })
    for produkt in lista:
        print(f"Nazwa: {produkt['nazwa_produktu']}\n  Link do produktu: {produkt['link']}\n")