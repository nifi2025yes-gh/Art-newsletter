import json
from bs4 import BeautifulSoup

def parse_met():
    try:
        with open("met.html", "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        
        exhibitions = []
        # The Met usually has articles or cards for exhibitions
        # This is a guess. Let's find all headers and links.
        for card in soup.find_all("div", class_="media-block__content"):
            title_tag = card.find("h3") or card.find("h2")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            
            date_tag = card.find("p")
            date_str = date_tag.get_text(strip=True) if date_tag else ""
            
            link = ""
            a_tag = card.find("a")
            if a_tag and a_tag.get("href"):
                link = "https://www.metmuseum.org" + a_tag["href"] if a_tag["href"].startswith("/") else a_tag["href"]
            
            exhibitions.append({"title": title, "date": date_str, "link": link})
        print("Met:", exhibitions[:3])
    except Exception as e:
        print("Met Error:", e)

def parse_tate():
    try:
        with open("tate.html", "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        
        exhibitions = []
        # Let's search for "card" or similar classes
        for el in soup.find_all("a", class_=lambda x: x and "card" in x.lower()):
            title_tag = el.find("div", class_=lambda x: x and "title" in x.lower())
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = "https://www.tate.org.uk" + el.get("href", "") if el.get("href", "").startswith("/") else el.get("href", "")
            exhibitions.append({"title": title, "link": link})
        print("Tate:", exhibitions[:3])
    except Exception as e:
        print("Tate Error:", e)

parse_met()
parse_tate()
