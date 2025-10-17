import sqlite3
from datetime import datetime
import locale
from bs4 import BeautifulSoup
from typing import List, Dict

from utils.helpers import fetch, remove_time_zone, generate_id, insert_to_db

locale.setlocale(locale.LC_ALL, 'id_ID')

def get_published_date(url: str) -> str:
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    time_raw = soup.find("p", class_='text-neutral-900 text-sm').get_text(strip=True)
    if time_raw:
        remove_timezone_time = remove_time_zone(time_raw).replace(' |', '')
        obj_date = datetime.strptime(remove_timezone_time, '%d %B %Y %H.%M')
        formatted_date = obj_date.strftime('%Y-%m-%d %H:%M')
        return formatted_date
    return ''

def parse_tempo(html: str) -> List[Dict]:
    conn = sqlite3.connect('./databases/tempo.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    soup = BeautifulSoup(html, "html.parser")
    headlines = []

    # Find all article elements containing headlines
    grid_section = soup.select_one("#hero > div > div.w-full.lg\:w-\[736px\] > div")
    if grid_section:
        a_tags = grid_section.find_all("a")
        for a_tag in a_tags:
            if a_tag and a_tag.get_text(strip=True):
                url = f'https://www.tempo.co/{a_tag["href"]}'
                headline = {
                    "source": "tempo",
                    "title": a_tag.get_text(strip=True),
                    "url": url,
                    "published_date": get_published_date(url),
                    "scraped_at": datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                headline["id"] = generate_id(
                    headline["source"],
                    headline["title"],
                    headline["url"],
                    headline["published_date"]
                )
                headlines.append(headline)
    insert_to_db(conn, cur, headlines)
    conn.close()
    return headlines
