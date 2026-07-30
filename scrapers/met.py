import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper
from datetime import datetime

class MetScraper(BaseScraper):
    """
    메트로폴리탄 미술관(The Met) 전시 정보를 수집합니다.
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "The Metropolitan Museum of Art"
        self.base_url = "https://www.metmuseum.org/exhibitions"

    def fetch_data(self) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(self.base_url, headers=headers, timeout=10)
        return response.text

    def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        exhibitions = []
        
        # 전시 카드 찾기
        for article in soup.find_all("article"):
            try:
                title_elem = article.find("div", role="heading")
                if not title_elem:
                    continue
                a_tag = title_elem.find("a")
                if not a_tag:
                    continue
                title = a_tag.get_text(strip=True)
                
                link = ""
                href = a_tag.get("href")
                if href:
                    if href.startswith("/"):
                        link = "https://www.metmuseum.org" + href
                    else:
                        link = href
                
                # 'exhibitions'가 포함되지 않은 링크는 건너뛰기
                if "exhibition" not in link.lower():
                    continue

                # 날짜 찾기
                date_str = "Dates not specified"
                for div in article.find_all("div"):
                    text = div.get_text(strip=True)
                    if "Through" in text or "2026" in text or "2027" in text or "Opens" in text:
                        date_str = text
                        break

                # 이미지 찾기
                image_url = ""
                img = article.find("img")
                if img:
                    image_url = img.get("src") or img.get("srcset", "").split(" ")[0]

                exhibitions.append({
                    "title": title,
                    "date": date_str,
                    "image_url": image_url,
                    "link": link
                })
            except Exception as e:
                print("Error parsing a Met exhibition:", e)

        # 중복 제거 및 최대 5개 반환
        unique_exhibitions = []
        seen = set()
        for exh in exhibitions:
            if exh["title"] not in seen:
                seen.add(exh["title"])
                unique_exhibitions.append(exh)
        
        return unique_exhibitions[:5]
