import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Any
from .base import BaseScraper

class MoriScraper(BaseScraper):
    """
    모리 미술관(Mori Art Museum) 전시 정보를 수집합니다.
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "Mori Art Museum, Tokyo"
        self.base_url = "https://www.mori.art.museum/en/exhibitions/"

    def fetch_data(self) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(self.base_url, headers=headers, timeout=10)
        return response.text

    def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        exhibitions = []
        
        for h in soup.find_all(["h2", "h3"]):
            a_tag = h.find_parent("a")
            if not a_tag:
                continue
                
            href = a_tag.get("href", "")
            title = h.get_text(strip=True)
            if not title or title.lower() in ["more pick-ups", "mori art museum online shop"]:
                continue

            link = urljoin(self.base_url, href)

            date_str = "Current / Upcoming"
            date_p = h.find_next_sibling("p")
            if date_p:
                date_str = date_p.get_text(strip=True)

            image_url = ""
            img = a_tag.find("img")
            if img:
                image_url = img.get("data-pcimg") or img.get("data-spimg") or img.get("src", "")
                if image_url:
                    image_url = urljoin(self.base_url, image_url)

            exhibitions.append({
                "title": title,
                "date": date_str,
                "image_url": image_url,
                "link": link
            })

        unique_exhibitions = []
        seen = set()
        for exh in exhibitions:
            if exh["title"] not in seen:
                seen.add(exh["title"])
                unique_exhibitions.append(exh)
        
        return unique_exhibitions[:5]
