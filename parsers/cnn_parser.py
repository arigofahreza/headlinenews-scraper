from datetime import datetime

from bs4 import BeautifulSoup
from typing import List, Dict


def parse_cnn(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    headlines = []

    # Find all article elements containing headlines
    grid_sections = soup.find_all("div", class_="grid")
    for section in grid_sections:
        # Ensure it matches the main layout (6 columns with gap)
        if "grid-cols-6" in section.get("class", []) and "gap-4" in section.get("class", []):
            articles = section.find_all("article", class_="flex-grow")
            for article in articles:
                a_tag = article.find("a", href=True)
                if a_tag and a_tag.get_text(strip=True):
                    headlines.append({
                        "source": "cnnindonesia",
                        "title": a_tag.get_text(strip=True),
                        "url": a_tag["href"]
                    })

    return headlines
