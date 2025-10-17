import sqlite3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict

from utils.helpers import fetch, remove_time_zone, generate_id, insert_to_db, format_month, get_db_path


def get_published_date(url: str) -> str:
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    time_raw = soup.find("div", class_='detail__date').get_text(strip=True)
    if time_raw:
        remove_timezone_time = remove_time_zone(time_raw)
        split_time_raw = remove_timezone_time.split(', ')
        obj_date = datetime.strptime(format_month(split_time_raw[1]), '%d %b %Y %H:%M')
        formatted_date = obj_date.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date
    return ''

def parse_detiknews() -> List[Dict]:
    db_path = get_db_path()
    conn = sqlite3.connect(f'{db_path}/detiknews.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    current_date = (datetime.now()).strftime('%m%%2F%d%%2F%Y')
    url_source = f'https://www.cnnindonesia.com/indeks/?date={current_date}'
    html_source = fetch(url_source)
    soup = BeautifulSoup(html_source, "html.parser")
    page_links = soup.select("div.pagination a")
    page_numbers = []
    for a in page_links:
        text = a.get_text(strip=True)
        if text.isdigit():
            page_numbers.append(int(text))
    max_page = max(page_numbers) if page_numbers else 1
    headlines = []
    for page in range(1, int(max_page) + 1):
        url_page = f'https://news.detik.com/indeks?page={page}&date={current_date}'
        html_page = fetch(url_page)
        soup_page = BeautifulSoup(html_page, "html.parser")
        grid_section = soup_page.select_one("#indeks-container")
        if grid_section:
            articles = grid_section.select("article.list-content__item")
            for article in articles:
                a_tags = article.find_all("a")
                for a_tag in a_tags:
                    if a_tag and a_tag.get_text(strip=True):
                        headline = {
                            "source": "detiknews",
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
    parse_detiknews()