import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict

from utils.helpers import fetch, remove_time_zone, generate_id, insert_to_db, format_month


def get_published_date(url: str) -> str:
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    time_raw = soup.select_one("[class*='text-cnn_grey']").get_text(strip=True)
    if time_raw:
        remove_timezone_time = remove_time_zone(time_raw)
        split_time_raw = remove_timezone_time.split(', ')
        obj_date = datetime.strptime(format_month(split_time_raw[1]), '%d %b %Y %H:%M')
        formatted_date = obj_date.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date
    return ''


def parse_cnn() -> List[Dict]:
    conn = sqlite3.connect('../databases/cnn.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    url = 'https://www.cnnindonesia.com/'
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    headlines = []

    # Find all article elements containing headlines
    grid_sections = soup.find_all("div", class_="grid")
    for section in grid_sections:
        # Ensure it matches the main layout (6 columns with gap)
        if "grid-cols-6" in section.get("class") and "gap-4" in section.get("class"):
            articles = section.find_all("article", class_="flex-grow")
            for article in articles:
                a_tag = article.find("a", href=True)
                if a_tag and a_tag.get_text(strip=True):
                    headline = {
                        "source": "cnnindonesia",
                        "title": a_tag.get_text(strip=True),
                        "url": a_tag["href"],
                        "published_date": get_published_date(a_tag['href']),
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
    parse_cnn()