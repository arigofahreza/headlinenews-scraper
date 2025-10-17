import sqlite3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict

from utils.helpers import fetch, remove_time_zone, generate_id, insert_to_db, format_month, get_db_path


def get_published_date(time_str: str) -> str:
    time_raw = remove_time_zone(format_month(time_str))
    if time_raw:
        date_part = time_raw.split(",")[1].strip()
        obj_date = datetime.strptime(date_part, '%d %B %Y %H:%M')
        formatted_date = obj_date.strftime('%Y-%m-%d %H:%M')
        return formatted_date
    return ''

def parse_tribun() -> List[Dict]:
    db_path = get_db_path()
    conn = sqlite3.connect(f'{db_path}/tribun.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    current_date = (datetime.now()).strftime('%Y-%m-%d')
    url_source = f'https://www.tribunnews.com/index-news/all?date={current_date}'
    html_source = fetch(url_source)
    soup = BeautifulSoup(html_source, "html.parser")
    pagination = soup.find("div", class_='paging')
    page_numbers = []
    for a in pagination:
        text = a.get('data-ci-pagination-page')
        if text and text.isdigit():
            page_numbers.append(int(text))
    max_page = max(page_numbers) if page_numbers else 1
    headlines = []
    for page in range(1, int(max_page) + 1):
        grid_section = soup.find('div', class_="pt10 pb10")
        if grid_section:
            li_tags = grid_section.find_all("li", class_="ptb15")
            for li_tag in li_tags:
                a_tags = li_tag.find_all("a")
                time_tag = li_tag.find('time', class_='grey')
                for a_tag in a_tags:
                    if a_tag and a_tag['title']:
                        headline = {
                            "source": "tribun",
                            "title": a_tag['title'],
                            "url": a_tag['href'],
                            "published_date": get_published_date(time_tag.get_text()),
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

if __name__ == '__main__':
    parse_tribun()