import sqlite3

from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime

from utils.helpers import fetch, remove_time_zone, generate_id, insert_to_db


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
        formatted_date = obj_date.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date
    return ''



def parse_kompas() -> List[Dict]:
    conn = sqlite3.connect('../databases/kompas.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    url = 'https://www.kompas.com/'
    html = fetch(url)
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
                headline = {
                    "source": "kompas",
                    "title": title_tag.get_text(strip=True),
                    "url": link_tag["href"],
                    "published_date": get_published_date(link_tag['href']),
                    "scraped_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

if __name__ == '__main__':
    parse_kompas()