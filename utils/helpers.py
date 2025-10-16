from datetime import datetime, timezone, date
import json
from pathlib import Path
from typing import List, Dict


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
