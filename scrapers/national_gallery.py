import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper

class NationalGalleryScraper(BaseScraper):
    """
    내셔널 갤러리(National Gallery, London) 전시 정보를 수집합니다.
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "National Gallery, London"
        self.base_url = "https://www.nationalgallery.org.uk/exhibitions"

    def fetch_data(self) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
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

            link = "https://www.nationalgallery.org.uk" + href if href.startswith("/") else href

            date_str = "Current / Upcoming"
            # 내셔널 갤러리는 보통 날짜가 a 태그 내 다른 p 또는 span에 위치
            date_elem = a_tag.find(class_=lambda x: x and "date" in x.lower())
            if not date_elem:
                # 텍스트로 유추
                for p in a_tag.find_all("p"):
                    if any(month in p.get_text() for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                        date_str = p.get_text(strip=True)
                        break
            else:
                date_str = date_elem.get_text(strip=True)

            image_url = ""
            img = a_tag.find("img")
            if img:
                image_url = img.get("src") or img.get("data-src", "")
            else:
                # 배경 이미지(div style)에서 추출
                bg_div = a_tag.find("div", style=lambda x: x and "background-image" in x)
                if bg_div:
                    style = bg_div["style"]
                    import re
                    match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
                    if match:
                        image_url = match.group(1)

            if image_url and image_url.startswith("/"):
                image_url = "https://www.nationalgallery.org.uk" + image_url

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
