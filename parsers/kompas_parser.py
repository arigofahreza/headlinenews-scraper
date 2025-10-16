from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime

from utils.helpers import fetch, remove_time_zone


def get_published_date(url: str) -> str:
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    time_raw = soup.find("div", class_='read__time').get_text(strip=True)
    if time_raw:
        split_time_raw = time_raw.split('- ')
        date_split = split_time_raw[1].split(', ')
        remove_timezone_time = remove_time_zone(date_split[1])
        str_date = date_split[0] + remove_timezone_time
        obj_date = datetime.strptime(str_date, '%d/%m/%Y%H:%M')
        formatted_date = obj_date.strftime('%Y-%m-%d %H:%M')
        return formatted_date
    return ''



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
                    "published_date": get_published_date(link_tag['href']),
                    "scraped_at": datetime.now().strftime('%Y-%m-%d %H:%M')
                })

    return headlines
