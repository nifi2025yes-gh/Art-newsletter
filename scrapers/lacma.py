import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper

class LACMAScraper(BaseScraper):
    """
    LACMA(Los Angeles County Museum of Art) 전시 정보를 수집합니다.
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "Los Angeles County Museum of Art (LACMA)"
        self.base_url = "https://www.lacma.org/art/exhibitions/current"

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
            a_tag = h.find_parent("a") or h.find("a")
            if not a_tag:
                continue
                
            href = a_tag.get("href", "")
            title = h.get_text(strip=True)
            if not title or title.lower() in ["exhibitions", "museum hours", "footer links"]:
                continue

            link = "https://www.lacma.org" + href if href.startswith("/") else href

            date_str = "Current / Upcoming"
            parent = h.find_parent("div", class_=lambda x: x and "content" in x.lower())
            if not parent:
                parent = h.find_parent("div")
            if parent:
                for date_div in parent.find_all("div"):
                    if any(month in date_div.get_text() for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "–"]):
                        date_str = date_div.get_text(strip=True)
                        break

            image_url = ""
            img = parent.find_previous_sibling("div")
            if img:
                img_tag = img.find("img")
                if img_tag:
                    image_url = img_tag.get("src") or img_tag.get("data-src", "")
                    if image_url.startswith("/"):
                        image_url = "https://www.lacma.org" + image_url

            # If image still empty, just find any img near the h tag
            if not image_url:
                container = h.find_parent("article") or h.find_parent("div", class_="views-row")
                if container:
                    img_tag = container.find("img")
                    if img_tag:
                        image_url = img_tag.get("src") or img_tag.get("data-src", "")
                        if image_url.startswith("/"):
                            image_url = "https://www.lacma.org" + image_url

            exhibitions.append({
                "title": title,
                "date": date_str,
                "image_url": image_url,
                "link": link
            })

        # 중복 제거
        unique_exhibitions = []
        seen = set()
        for exh in exhibitions:
            if exh["title"] not in seen:
                seen.add(exh["title"])
                unique_exhibitions.append(exh)
        
        return unique_exhibitions[:5]
