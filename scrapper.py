import os
import sqlite3

import requests
from datetime import datetime, timezone
from typing import List, Dict

from parsers.cnn_parser import parse_cnn
from parsers.detiknews_parser import parse_detiknews
from parsers.kompas_parser import parse_kompas
from parsers.liputan6_parser import parse_liputan6
from parsers.tempo_parser import parse_tempo
from utils.helpers import fetch

SITES = [
    {"name": "kompas", "url": "https://www.kompas.com/", "parser": parse_kompas},
    {"name": "detiknews", "url": "https://news.detik.com/", "parser": parse_detiknews},
    {"name": "tempo", "url": "https://www.tempo.co/", "parser": parse_tempo},
    {"name": "cnnindonesia", "url": "https://www.cnnindonesia.com/", "parser": parse_cnn},
    {"name": "liputan6", "url": "https://www.liputan6.com/", "parser": parse_liputan6},
]


def table_creator(file: str):
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    # Wrap schema creation in one transaction
    cur.executescript("""
    BEGIN;

    CREATE TABLE IF NOT EXISTS headlines (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE,
        published_date DATETIME,
        scraped_at DATETIME NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_headlines_source
        ON headlines (source);

    CREATE INDEX IF NOT EXISTS idx_headlines_published_date
        ON headlines (published_date);

    CREATE INDEX IF NOT EXISTS idx_headlines_scraped_at
        ON headlines (scraped_at);

    CREATE INDEX IF NOT EXISTS idx_headlines_source_pubdate
        ON headlines (source, published_date);

    COMMIT;
    """)

    conn.close()


def scrape_news_today() -> List[Dict]:
    """Scrape the configured sites and return items whose published_time is today (UTC) when available.

    If a parser doesn't provide published_time, include the item but with published_time set to None.
    """
    items = []
    today = datetime.now(timezone.utc).date()
    for site in SITES:
        try:
            html = fetch(site['url'])
            parsed = site['parser'](html)
            print(parsed)
            for it in parsed:
                # If published_time is present, try to parse date and compare
                pt = it.get('published_time')
                if pt:
                    try:
                        dt = datetime.fromisoformat(pt)
                        if dt.date() == today:
                            items.append(it)
                    except Exception:
                        # unknown format, include anyway
                        items.append(it)
                else:
                    items.append(it)
        except Exception as e:
            # continue on errors; in production log properly
            print(f"Failed to fetch {site['name']}: {e}")
    return items


if __name__ == '__main__':
    for filename in os.listdir('./databases'):
        table_creator(f'./databases/{filename}')
    items = scrape_news_today()
    print(f"Wrote {len(items)} items to data/latest_headlines.json")
