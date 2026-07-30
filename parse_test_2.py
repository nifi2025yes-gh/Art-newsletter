import json
from bs4 import BeautifulSoup
from scrapers.met import MetScraper
from scrapers.tate import TateScraper

def test():
    with open("met.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    for article in soup.find_all("article"):
        a_tag = article.find("a", href=True)
        title = a_tag.get_text(strip=True) if a_tag else "No title"
        print("Met raw article title:", title)
    
    with open("tate.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    for a in soup.find_all("a", href=True):
        if "exhibition" in a["href"].lower():
            print("Tate raw link:", a["href"], a.get_text(strip=True)[:50])

test()
