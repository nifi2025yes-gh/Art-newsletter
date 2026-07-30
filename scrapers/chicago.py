import requests
import json
from typing import List, Dict, Any
from .base import BaseScraper
from datetime import datetime

class ChicagoScraper(BaseScraper):
    """
    시카고 미술관(Art Institute of Chicago) 전시 정보를 수집합니다. (Public API 활용)
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "Art Institute of Chicago"
        self.base_url = "https://api.artic.edu/api/v1/exhibitions?limit=5&status=current"

    def fetch_data(self) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(self.base_url, headers=headers, timeout=10)
        return response.text

    def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
        # html_content is actually JSON string here
        try:
            data = json.loads(html_content)
            exhibits = data.get("data", [])
        except Exception:
            exhibits = []

        exhibitions = []
        for exh in exhibits:
            title = exh.get("title", "")
            if not title:
                continue

            link = exh.get("web_url") or f"https://www.artic.edu/exhibitions/{exh.get('id')}"
            image_url = exh.get("image_url", "")
            
            start = exh.get("aic_start_at", "")
            end = exh.get("aic_end_at", "")
            
            date_str = "Current"
            try:
                if start and end:
                    start_dt = datetime.strptime(start[:10], "%Y-%m-%d")
                    end_dt = datetime.strptime(end[:10], "%Y-%m-%d")
                    date_str = f"{start_dt.strftime('%b %d, %Y')} – {end_dt.strftime('%b %d, %Y')}"
            except Exception:
                pass

            exhibitions.append({
                "title": title,
                "date": date_str,
                "image_url": image_url,
                "link": link
            })
            
        return exhibitions[:5]
