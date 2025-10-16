import requests
from datetime import datetime, timezone
from typing import List, Dict

from parsers.cnn_parser import parse_cnn
from parsers.kompas_parser import parse_kompas
from utils.helpers import save_json

SITES = [
    # {"name": "kompas", "url": "https://www.kompas.com/", "parser": parse_kompas},
    # {"name": "detik", "url": "https://www.detik.com/", "parser": parse_detik},
    # {"name": "tempo", "url": "https://www.tempo.co/", "parser": parse_tempo},
    {"name": "cnnindonesia", "url": "https://www.cnnindonesia.com/", "parser": parse_cnn},
    # {"name": "liputan6", "url": "https://www.liputan6.com/", "parser": parse_liputan6},
]


def fetch(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    }
    resp = requests.get(url, timeout=10, headers=headers)
    resp.raise_for_status()
    return resp.text


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
    items = scrape_news_today()
    # save_json(items, 'data/latest_headlines.json')
    print(f"Wrote {len(items)} items to data/latest_headlines.json")
