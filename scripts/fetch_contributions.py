"""Busca o grid público de contribuições do GitHub (HTML) e salva como JSON."""
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "samueljs0"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch() -> list[dict]:
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    cells = soup.select("td.ContributionCalendar-day") or soup.select("rect.ContributionCalendar-day")
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        count = 0
        tooltip_id = cell.get("id")
        if tooltip_id:
            tooltip = soup.find("tool-tip", attrs={"for": tooltip_id})
            if tooltip:
                match = re.search(r"(\d+|No)\s+contribution", tooltip.get_text())
                if match:
                    count = 0 if match.group(1) == "No" else int(match.group(1))
        if date:
            days.append({"date": date, "level": int(level) if level is not None else 0, "count": count})

    return days


def main() -> None:
    days = fetch()
    out_path = DATA_DIR / "contributions.json"
    out_path.write_text(json.dumps(days, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[fetch_contributions] {len(days)} dias salvos em {out_path}")


if __name__ == "__main__":
    main()
