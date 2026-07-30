import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseScraper

class MoMAScraper(BaseScraper):
    """
    MoMA(Museum of Modern Art) 전시 정보를 가져오는 스크래퍼입니다.
    현재는 MVP를 위한 샘플(더미) 데이터를 반환하도록 구성되어 있습니다.
    실제 배포 시에는 requests/BeautifulSoup을 사용하여 실제 HTML을 파싱하도록 수정합니다.
    """
    def __init__(self):
        super().__init__()
        self.museum_name = "MoMA (The Museum of Modern Art)"
        self.base_url = "https://www.moma.org/calendar/exhibitions"

    def fetch_data(self) -> str:
        # 실제 환경에서는 requests.get(self.base_url) 사용
        # JS 렌더링이 필요하다면 Playwright 도입 고려
        return "<html>Dummy HTML for MoMA</html>"

    def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
        # 테스트를 위한 더미 데이터 반환
        return [
            {
                "title": "Ed Ruscha / Now Then",
                "date": "Sep 10, 2023 – Jan 13, 2024",
                "image_url": "https://www.moma.org/d/assets/W1siZiIsIjIwMjMvMDgvMTYvNDd4dDFwazZwcV9SdV9QbGF5X1Zlbl8wMTRfQ1IuanBnIl0sWyJwIiwiY29udmVydCIsIi1xdWFsaXR5IDkwIC1yZXNpemUgMjAwMHgyMDAwXHUwMDNlIl1d/Ru_Play_Ven_014_CR.jpg",
                "link": "https://www.moma.org/calendar/exhibitions/5582"
            },
            {
                "title": "Picasso in Fontainebleau",
                "date": "Oct 8, 2023 – Feb 17, 2024",
                "image_url": "https://www.moma.org/d/assets/W1siZiIsIjIwMjMvMDYvMDgvNWp2cXN0Ym13aF9QaWNhc3NvX0ZvbnRhaW5lYmxlYXVfQ1IuanBnIl0sWyJwIiwiY29udmVydCIsIi1xdWFsaXR5IDkwIC1yZXNpemUgMjAwMHgyMDAwXHUwMDNlIl1d/Picasso_Fontainebleau_CR.jpg",
                "link": "https://www.moma.org/calendar/exhibitions/5583"
            }
        ]
