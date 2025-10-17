import sqlite3

from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime, timedelta

from utils.helpers import fetch, remove_time_zone, generate_id, insert_to_db, get_db_path


def get_published_date(url: str) -> str:
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    time_raw = soup.find("div", class_='read__time').get_text(strip=True)
    if time_raw:
        split_time_raw = time_raw.split('- ')
        date_split = split_time_raw[1].split(', ')
        remove_timezone_time = remove_time_zone(date_split[1])
        str_date = date_split[0] + remove_timezone_time
        obj_date = datetime.strptime(str_date.replace('Diperbarui ', ''), '%d/%m/%Y%H:%M')
        formatted_date = obj_date.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date
    return ''



def parse_kompas() -> List[Dict]:
    db_path = get_db_path()
    conn = sqlite3.connect(f'{db_path}/kompas.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    current_date = (datetime.now()).strftime('%Y-%m-%d')
    url_source = f'https://indeks.kompas.com/?site=all&date={current_date}'
    html_source = fetch(url_source)
    soup = BeautifulSoup(html_source, "html.parser")
    paginations = soup.find_all("div", class_='paging__item')
    max_page = 1
    if paginations:
        for pagination in paginations:
            last_link = pagination.find("a", class_="paging__link paging__link--last")
            if last_link:
                max_page = last_link.get("data-ci-pagination-page")
    headlines = []
    for page in range(1, int(max_page) + 1):
        url_page = f'https://indeks.kompas.com/?site=all&date={current_date}&page={page}'
        html_page = fetch(url_page)
        soup_page = BeautifulSoup(html_page, "html.parser")
        sections = soup_page.find_all("div", class_="articleItem")
        for section in sections:
            link_tag = section.find("a", href=True)
            title_tag = section.find("h2", class_="articleTitle")
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