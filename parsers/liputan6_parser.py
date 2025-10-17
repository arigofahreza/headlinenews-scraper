import sqlite3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict

from utils.helpers import fetch, remove_time_zone, generate_id, insert_to_db, format_month, get_db_path


def get_published_date(time_str: str) -> str:
    remove_timezone_time = remove_time_zone(format_month(time_str))
    obj_date = datetime.strptime(f'{remove_timezone_time}', '%d %b %Y %H:%M')
    formatted_date = obj_date.strftime('%Y-%m-%d %H:%M')
    return formatted_date

def parse_liputan6() -> List[Dict]:
    db_path = get_db_path()
    conn = sqlite3.connect(f'{db_path}/liputan6.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    current_date = (datetime.now()).strftime('%Y/%m/%d')
    url_source = f"https://www.liputan6.com/news/indeks/{current_date}"
    html_source = fetch(url_source)
    soup = BeautifulSoup(html_source, "html.parser")
    pagination = soup.find("div", class_='simple-pagination__container')
    max_page = 1
    if pagination:
        li_pages = pagination.find_all("li", class_="simple-pagination__page-number")
        for li in li_pages:
            max_page = li.get("data-page")
    headlines = []
    for page in range(1, int(max_page) + 1):
        url_page = f'https://www.liputan6.com/news/indeks/{current_date}?page={page}'
        html_page = fetch(url_page)
        soup_page = BeautifulSoup(html_page, "html.parser")
        grid_section = soup_page.select_one("#indeks-articles > div.articles--list.articles--list_rows")
        if grid_section:
            a_tags = grid_section.find_all("a", class_='articles--rows--item__title-link')
            for a_tag in a_tags:
                if a_tag and a_tag.get_text(strip=True):
                    time_tag = grid_section.find('time', class_='articles--rows--item__time timeago')
                    headline = {
                        "source": "liputan6",
                        "title": a_tag['title'],
                        "url": a_tag["href"],
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
    parse_liputan6()