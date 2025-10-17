import sqlite3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict

from utils.helpers import fetch, remove_time_zone, generate_id, insert_to_db, format_month, get_db_path


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
    db_path = get_db_path()
    conn = sqlite3.connect(f'{db_path}/cnn.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    current_date = (datetime.now()).strftime('%Y/%m/%d')
    url_source = f'https://www.cnnindonesia.com/indeks/?date={current_date}'
    html = fetch(url_source)
    soup = BeautifulSoup(html, "html.parser")
    page_links = soup.select("div.justify-center a[href*='page=']")
    page_numbers = []
    for a in page_links:
        text = a.get_text(strip=True)
        if text.isdigit():
            page_numbers.append(int(text))
    max_page = max(page_numbers) if page_numbers else 1
    headlines = []
    for page in range(1, int(max_page)+1):
        url_page = f'https://www.cnnindonesia.com/indeks/?date={current_date}&page={page}'
        html_page = fetch(url_page)
        soup_page = BeautifulSoup(html_page, "html.parser")
        grid_sections = soup_page.find_all("div", class_="flex flex-col gap-5")
        for section in grid_sections:
            articles = section.find_all("article", class_="flex-grow")
            for article in articles:
                a_tag = article.find("a", href=True)
                h2_tag = article.find('h2')
                if a_tag and h2_tag:
                    headline = {
                        "source": "cnnindonesia",
                        "title": h2_tag.get_text(),
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