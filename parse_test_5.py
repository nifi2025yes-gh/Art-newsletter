import sys; sys.stdout.reconfigure(encoding='utf-8')
from scrapers.national_gallery import NationalGalleryScraper
from scrapers.vam import VAMScraper

def test():
    print("Testing National Gallery:")
    t1 = NationalGalleryScraper()
    data1 = t1.parse_data(open("national_gallery.html", "r", encoding="utf-8").read())
    for d in data1: print(d["title"])

    print("\nTesting V&A:")
    t2 = VAMScraper()
    data2 = t2.parse_data(open("vam.html", "r", encoding="utf-8").read())
    for d in data2: print(d["title"])

test()
