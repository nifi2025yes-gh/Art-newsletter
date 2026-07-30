import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper
from datetime import datetime

class LouvreScraper(BaseScraper):
    """
    루브르 박물관(Louvre) 전시 정보를 수집합니다.
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "The Louvre"
        self.base_url = "https://www.louvre.fr/en/what-s-on/exhibitions"

    def fetch_data(self) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(self.base_url, headers=headers, timeout=10)
        return response.text

    def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        exhibitions = []
        
        # Louvre는 Card_Main_title 안에 a 태그로 제목과 링크를 제공
        for title_tag in soup.find_all(["h2", "h3"]):
            try:
                a_tag = title_tag.find("a")
                if not a_tag or not a_tag.get("href"):
                    continue
                
                href = a_tag["href"]
                if "exhibition" not in href.lower():
                    continue

                title = a_tag.get_text(strip=True)
                if not title:
                    continue

                link = "https://www.louvre.fr" + href if href.startswith("/") else href

                # subtitle과 date는 형제 p 태그들에 있음
                parent_div = title_tag.parent
                date_str = "Current / Upcoming"
                
                date_tag = parent_div.find("p", class_=lambda x: x and "date" in x.lower())
                if date_tag:
                    date_str = date_tag.get_text(strip=True)

                # 이미지는 상위 컨테이너 어딘가에 있겠지만, 없으면 빈 값으로 처리
                image_url = ""
                card_container = parent_div.find_parent("div", class_=lambda x: x and "card" in x.lower())
                if card_container:
                    img = card_container.find("img")
                    if img:
                        image_url = img.get("src") or img.get("data-src", "")

                exhibitions.append({
                    "title": title,
                    "date": date_str,
                    "image_url": image_url,
                    "link": link
                })
            except Exception as e:
                pass

        # 중복 제거
        unique_exhibitions = []
        seen = set()
        for exh in exhibitions:
            if exh["title"] not in seen:
                seen.add(exh["title"])
                unique_exhibitions.append(exh)
        
        return unique_exhibitions[:5]
