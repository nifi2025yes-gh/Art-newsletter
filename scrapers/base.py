from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    """
    모든 미술관 스크래퍼가 상속받아야 하는 기본 클래스입니다.
    HERMES.md의 '구조와 확장성' 원칙에 따라 추상화되었습니다.
    """

    def __init__(self):
        self.museum_name = "Unknown"
        self.base_url = ""

    @abstractmethod
    def fetch_data(self) -> str:
        """
        웹페이지의 HTML 내용을 가져옵니다.
        """
        pass

    @abstractmethod
    def parse_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        HTML에서 전시 정보를 추출하여 딕셔너리 리스트로 반환합니다.
        반환 형식:
        [
            {
                "title": "Exhibition Title",
                "date": "2023.10.01 - 2024.01.15",
                "image_url": "https://...",
                "link": "https://..."
            }, ...
        ]
        """
        pass

    def get_exhibitions(self) -> List[Dict[str, Any]]:
        """
        데이터를 가져오고 파싱하여 최종 결과를 반환하는 템플릿 메서드입니다.
        """
        html = self.fetch_data()
        if html:
            return self.parse_data(html)
        return []
