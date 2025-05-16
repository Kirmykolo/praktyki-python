from bs4 import BeautifulSoup
from requests import get

URL = 'https://www.onet.pl/'

page = get(URL)

artykuly = BeautifulSoup(page.content, 'html.parser')

for artykul in artykuly.find_all('h3'):
    print(artykul.text.strip())
    break