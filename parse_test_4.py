import sys; sys.stdout.reconfigure(encoding='utf-8')
from scrapers.louvre import LouvreScraper

def test():
    t = LouvreScraper()
    html = open("louvre.html", "r", encoding="utf-8").read()
    data = t.parse_data(html)
    print("Louvre data length:", len(data))
    for d in data: print(d["title"])

test()
