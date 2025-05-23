from bs4 import BeautifulSoup
from requests import get
import csv
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

page_number = 1

base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie,rynek-wtorny/slaskie/czestochowa/czestochowa/czestochowa?page="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


with open("plik1.csv", "w",newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Numer", "Link"])

    while page_number <= 26:
        url = f"{base_url}{page_number}"
        print(f"Pobieram strone {page_number} {url}")

        time.sleep(2)

        page=get(url, headers=headers)
        soup=BeautifulSoup(page.content, "html.parser")

        listings =soup.find_all("article", attrs={"data-cy": "listing-item"})

        if not listings: 
            print("Nie znaleziono strony ")
            break
        else:
            for i, offert in enumerate(listings, start= (page_number - 1) ):
                offert_link = offert.find("a", attrs={"data-cy": "listing-item-link"}) 

                if offert_link:
                    writer.writerow([i, offert_link.get("href")])
                    print(offert_link.get("href"))
                else:
                    print("nie znaleziono linku dla oferty nr: ", i)


            time.sleep(2)
            page_number+=1