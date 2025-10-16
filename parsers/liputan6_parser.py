from datetime import datetime
import locale
from bs4 import BeautifulSoup
from typing import List, Dict

from utils.helpers import fetch, remove_time_zone

locale.setlocale(locale.LC_ALL, 'id_ID')

def get_published_date(url: str) -> str:
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    time_raw = soup.find("span", class_='read-page-box__author__updated').get_text(strip=True)
    if time_raw:
        remove_timezone_time = remove_time_zone(time_raw).replace('Diterbitkan ', '')
        split_time_raw = remove_timezone_time.split(', ')
        obj_date = datetime.strptime(f'{split_time_raw[0]} {split_time_raw[1]}', '%d %B %Y %H:%M')
        formatted_date = obj_date.strftime('%Y-%m-%d %H:%M')
        return formatted_date
    return ''

def parse_liputan6(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    headlines = []

    # Find all article elements containing headlines
    grid_section = soup.select_one("body > main > div.headline > div.headline--main")
    if grid_section:
        a_tags = grid_section.find_all("a")
        for a_tag in a_tags:
            if a_tag and a_tag.get_text(strip=True):
                headlines.append({
                    "source": "liputan6",
                    "title": a_tag.get_text(strip=True),
                    "url": a_tag["href"],
                    "published_date": get_published_date(a_tag['href']),
                    "scraped_at": datetime.now().strftime('%Y-%m-%d %H:%M')
                })

    return headlines
