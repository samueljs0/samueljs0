"""Monta o grid de contribuições a partir dos commits reais do usuário (via `gh api search/commits`),
em vez de raspar só o calendário público do perfil — assim inclui repositórios privados que o
token autenticado (`gh auth login`) tem acesso, que é o que normalmente falta na página pública."""
import json
import subprocess
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

USERNAME = "samueljs0"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WEEKS = 53


def week_start() -> date:
    end = date.today()
    start = end - timedelta(weeks=WEEKS - 1)
    while start.weekday() != 6:  # volta até o domingo anterior (Mon=0 ... Sun=6)
        start -= timedelta(days=1)
    return start


def fetch_commit_dates(since: date) -> list[str]:
    query = f"author:{USERNAME}+author-date:>{since.isoformat()}"
    proc = subprocess.run(
        ["gh", "api", "--paginate", f"search/commits?q={query}&per_page=100",
         "--jq", ".items[] | {sha, date: .commit.author.date}"],
        capture_output=True, text=True, check=True,
    )
    seen_sha = set()
    dates = []
    for line in proc.stdout.splitlines():
        item = json.loads(line)
        if item["sha"] in seen_sha:
            continue
        seen_sha.add(item["sha"])
        dates.append(item["date"])
    return dates


def levels_for(counts: dict[str, int]) -> dict[str, int]:
    nonzero = sorted(v for v in counts.values() if v > 0)
    if not nonzero:
        return {d: 0 for d in counts}
    n = len(nonzero)
    t1 = nonzero[int(n * 0.25)]
    t2 = nonzero[int(n * 0.50)]
    t3 = nonzero[int(n * 0.75)]

    def level(v: int) -> int:
        if v == 0:
            return 0
        if v <= t1:
            return 1
        if v <= t2:
            return 2
        if v <= t3:
            return 3
        return 4

    return {d: level(v) for d, v in counts.items()}


def main() -> None:
    since = week_start()
    today = date.today()

    counts = defaultdict(int)
    d = since
    while d <= today:
        counts[d.isoformat()] = 0
        d += timedelta(days=1)

    for raw_date in fetch_commit_dates(since - timedelta(days=1)):
        day = datetime.fromisoformat(raw_date).date().isoformat()
        if day in counts:
            counts[day] += 1

    day_levels = levels_for(counts)
    days = [
        {"date": d, "level": day_levels[d], "count": c}
        for d, c in sorted(counts.items())
    ]

    out_path = DATA_DIR / "contributions.json"
    out_path.write_text(json.dumps(days, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(c for c in counts.values())
    print(f"[fetch_contributions] {len(days)} dias, {total} commits reais salvos em {out_path}")


if __name__ == "__main__":
    main()
