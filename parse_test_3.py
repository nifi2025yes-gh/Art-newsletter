import json
from scrapers.met import MetScraper
from scrapers.tate import TateScraper

def test():
    met = MetScraper()
    with open("met.html", "r", encoding="utf-8") as f:
        html = f.read()
    data = met.parse_data(html)
    print("Met data length:", len(data))
    for d in data: print(d["title"])

test()
