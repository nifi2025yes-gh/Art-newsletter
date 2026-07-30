import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapers import MoMAScraper
from templates import render_newsletter

def test_moma_scraper():
    scraper = MoMAScraper()
    exhibitions = scraper.get_exhibitions()
    
    assert len(exhibitions) > 0
    assert "title" in exhibitions[0]
    assert "date" in exhibitions[0]
    assert "image_url" in exhibitions[0]
    assert "link" in exhibitions[0]

def test_render_newsletter():
    dummy_data = {
        "Test Museum": [
            {
                "title": "Test Exhibition",
                "date": "2023-01-01 to 2023-12-31",
                "image_url": "http://example.com/image.jpg",
                "link": "http://example.com"
            }
        ]
    }
    html = render_newsletter(dummy_data)
    
    assert "Test Museum" in html
    assert "Test Exhibition" in html
    assert "2023-01-01 to 2023-12-31" in html
