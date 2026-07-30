import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper
from datetime import datetime

class TateScraper(BaseScraper):
    """
    테이트 모던(Tate Modern) 전시 정보를 수집합니다.
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "Tate Modern"
        self.base_url = "https://www.tate.org.uk/whats-on?gallery=tate-modern&type=exhibition"

    def fetch_data(self) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(self.base_url, headers=headers, timeout=10)
        return response.text

    def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        exhibitions = []
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/whats-on/tate-modern/" not in href:
                continue
            
            # 메인 페이지 링크는 제외
            if href.endswith("/whats-on/tate-modern") or href.endswith("/whats-on/tate-modern/"):
                continue

            try:
                title_elem = a_tag.find('h2') or a_tag.find('h3') or a_tag.find(class_=lambda x: x and 'title' in x.lower())
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                if not title or len(title) < 3: continue

                link = "https://www.tate.org.uk" + href if href.startswith("/") else href

                image_url = ""
                noscript = a_tag.find("noscript")
                if noscript and noscript.find("img"):
                    image_url = noscript.find("img").get("src", "")
                
                if not image_url or "placeholder" in image_url:
                    source = a_tag.find("source")
                    if source and source.get("srcset"):
                        image_url = source.get("srcset").split(" ")[0].strip()
                
                if not image_url or "placeholder" in image_url:
                    img = a_tag.find("img")
                    if img:
                        image_url = img.get("src") or img.get("data-src", "")

                date_str = "Current / Upcoming"
                date_elem = a_tag.find(class_=lambda x: x and 'date' in x.lower())
                if date_elem:
                    date_str = date_elem.get_text(strip=True)

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
            if exh["title"] and exh["title"] not in seen:
                seen.add(exh["title"])
                unique_exhibitions.append(exh)
        
        return unique_exhibitions[:5]
