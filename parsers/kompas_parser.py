from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime


def get_published_date(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")



def parse_kompas(html: str) -> List[Dict]:
    """Parse a Kompas listing page and return list of items with title, url, published_time (ISO)"""
    soup = BeautifulSoup(html, "html.parser")
    headlines = []

    # Find all sections containing headline groups (slider + grid)
    sections = soup.find_all("div", class_="hlWrap")
    for section in sections:
        # Each hlItem is one news card
        items = section.find_all("div", class_="hlItem")
        for item in items:
            link_tag = item.find("a", href=True)
            title_tag = item.find("h1", class_="hlTitle")

            if link_tag and title_tag:
                headlines.append({
                    "source": "kompas",
                    "title": title_tag.get_text(strip=True),
                    "url": link_tag["href"],
                    "scraped_at": datetime.now()
                })

    return headlines
