import hashlib
import os

import requests


def fetch(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    }
    resp = requests.get(url, timeout=10, headers=headers)
    resp.raise_for_status()
    return resp.text

def remove_time_zone(input_time: str) -> str:
    if 'WIB' or 'WITA' or 'WIT' in str:
        return input_time.replace('WIB', '').replace('WITA', '').replace('WIT', '').strip()
    return input_time

def insert_to_db(conn, cur, headlines):
    cur.executemany("""
        INSERT OR IGNORE INTO news_articles (id, source, title, url, published_date, scraped_at)
        VALUES (:id, :source, :title, :url, :published_date, :scraped_at)
        """, headlines)
    conn.commit()

def generate_id(source, title, url, published_date):
    raw_key = f"{source}|{title}|{url}|{published_date}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

def format_month(date_str: str):
    month_map = {
        'Jan': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Apr',
        'Mei': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Agu': 'Aug',
        'Sep': 'Sep', 'Okt': 'Oct', 'Nov': 'Nov', 'Des': 'Dec'
    }

    for indo, eng in month_map.items():
        if indo in date_str:
            date_str = date_str.replace(indo, eng)
            break
    return date_str

def get_db_path():
    current_directory = os.getcwd()
    db_path = f'{current_directory}/dags/headlinenews-scraper/databases'
    return db_path