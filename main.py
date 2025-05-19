from bs4 import BeautifulSoup
from requests import get
import sys

sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://www.onet.pl/'

page = get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

# Pobranie wszystkich artykułów
artykuly = soup.find_all("a", class_='Common_linkCardLink__cN081 SectionLink_linkStyle__xYsXd')

# Filtrowanie tylko tych, które należą do sekcji "wiadomości"
for artykul in artykuly:
    data_gtm = artykul.get("data-gtm", "")  # Pobieramy atrybut "data-gtm"
    
    if "news_" in data_gtm:  # Sprawdzamy, czy artykuł należy do sekcji "wiadomości"
        naglowek = artykul.find('h3', class_='TitleWrapper_titleWrapper__7S_PA')
        if naglowek:
            print(naglowek.text.strip())