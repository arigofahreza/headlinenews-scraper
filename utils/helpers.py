from datetime import datetime, timezone, date
import json
from pathlib import Path
from typing import List, Dict

import requests


def today_utc_date() -> date:
    return datetime.now(timezone.utc).date()


def save_json(data: List[Dict], path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: str):
    p = Path(path)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


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
