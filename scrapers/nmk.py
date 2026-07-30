import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper

class NMKScraper(BaseScraper):
    """
    국립중앙박물관(National Museum of Korea) 전시 정보를 수집합니다.
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "National Museum of Korea (NMK)"
        self.base_url = "https://www.museum.go.kr/site/eng/exhiSpecialTheme/list/current"

    def fetch_data(self) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(self.base_url, headers=headers, timeout=10)
        return response.text

    def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        exhibitions = []
        
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href", "")
            if "view" not in href.lower() or "menuid=current" not in href.lower():
                continue
                
            parent_li = a_tag.find_parent("li")
            if not parent_li:
                continue

            info_div = parent_li.find("div", class_="info")
            if not info_div:
                continue
                
            title_tag = info_div.find("strong")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            if not title:
                continue

            link = "https://www.museum.go.kr" + href if href.startswith("/") else href

            date_str = "Current / Upcoming"
            info_list = parent_li.find("ul", class_="info-list")
            if info_list:
                for li in info_list.find_all("li"):
                    if "Date" in li.get_text():
                        p_tag = li.find("p")
                        if p_tag:
                            date_str = p_tag.get_text(strip=True).replace("\\n", "").replace("\\t", "").replace("\\r", "")
                        break

            image_url = ""
            img_box = parent_li.find("div", class_="img-box")
            if img_box:
                img_tag = img_box.find("img")
                if img_tag:
                    src = img_tag.get("src") or img_tag.get("data-src", "")
                    # skip dummy onerror images
                    if "btn_more_report" not in src:
                        image_url = "https://www.museum.go.kr" + src if src.startswith("/") else src
            
            # If still no image, find any img inside the li
            if not image_url:
                imgs = parent_li.find_all("img")
                for img in imgs:
                    src = img.get("src") or ""
                    if src and "btn" not in src.lower():
                        image_url = "https://www.museum.go.kr" + src if src.startswith("/") else src
                        break

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
