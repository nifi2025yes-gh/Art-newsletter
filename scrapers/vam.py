import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper

class VAMScraper(BaseScraper):
    """
    빅토리아 앤 알버트 박물관(V&A Museum) 전시 정보를 수집합니다.
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "Victoria and Albert Museum (V&A)"
        self.base_url = "https://www.vam.ac.uk/exhibitions"

    def fetch_data(self) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
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
            if "/exhibitions/" not in href.lower():
                continue

            title = h.get_text(strip=True)
            if not title:
                continue

            link = "https://www.vam.ac.uk" + href if href.startswith("/") else href

            date_str = "Current / Upcoming"
            # V&A는 p 요소로 날짜나 부제목을 나타내는 경우가 많음
            date_elem = a_tag.find(class_=lambda x: x and "date" in x.lower())
            if not date_elem:
                for p in a_tag.find_all("p"):
                    if any(month in p.get_text() for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Until", "Opens"]):
                        date_str = p.get_text(strip=True)
                        break
            else:
                date_str = date_elem.get_text(strip=True)

            image_url = ""
            img = a_tag.find("img")
            if img:
                image_url = img.get("src") or img.get("data-src", "")
                if image_url.startswith("/"):
                    image_url = "https://www.vam.ac.uk" + image_url

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
