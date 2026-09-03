"""Gera o card de tecnologias (barra + legenda) a partir de data/stats.json."""
import json
from pathlib import Path


def escape(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

WIDTH = 430
BG = "#0d1117"
BORDER = "#30363d"
TITLE_COLOR = "#9fb3c8"
TEXT_COLOR = "#c9d1d9"
PCT_COLOR = "#8b949e"
OTHER_COLOR = "#8b949e"

MAX_LANGS = 8
BAR_HEIGHT = 10
BAR_Y = 74
ROW_HEIGHT = 26
ROWS_START_Y = BAR_Y + 34
COLS = 2
COL_WIDTH = (WIDTH - 48) / COLS


def top_languages(languages: list[dict]) -> list[dict]:
    shown = languages[:MAX_LANGS]
    rest_pct = round(sum(l["pct"] for l in languages[MAX_LANGS:]), 2)
    if rest_pct > 0:
        shown = shown + [{"name": "Outras", "color": OTHER_COLOR, "pct": rest_pct}]
    return shown


def build_bar(languages: list[dict]) -> str:
    x = 24.0
    segments = []
    for lang in languages:
        w = (WIDTH - 48) * lang["pct"] / 100
        segments.append(f'<rect x="{x:.1f}" y="{BAR_Y}" width="{w:.2f}" height="{BAR_HEIGHT}" fill="{lang["color"]}"/>')
        x += w
    return "\n  ".join(segments)


def build_legend(languages: list[dict]) -> str:
    rows = []
    for i, lang in enumerate(languages):
        col = i % COLS
        row = i // COLS
        x = 24 + col * COL_WIDTH
        y = ROWS_START_Y + row * ROW_HEIGHT
        label = f'{escape(lang["name"])} {lang["pct"]:.2f}%'
        rows.append(f"""
  <g transform="translate({x:.1f},{y})">
    <circle cx="4" cy="-4" r="4" fill="{lang["color"]}"/>
    <text class="lang" x="14" y="0">{label}</text>
  </g>""")
    return "".join(rows)


def build_svg(languages: list[dict]) -> str:
    shown = top_languages(languages)
    n_rows = -(-len(shown) // COLS)  # ceil
    height = ROWS_START_Y + n_rows * ROW_HEIGHT + 6

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <style>
    .title {{ font: 700 18px 'Courier New', monospace; fill: {TITLE_COLOR}; }}
    .prompt {{ font: 400 14px 'Courier New', monospace; fill: #6e7681; }}
    .lang {{ font: 400 14px 'Courier New', monospace; fill: {TEXT_COLOR}; }}
  </style>
  <rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <text class="prompt" x="24" y="34">samuel@github:~$</text>
  <text class="title" x="24" y="60">tecnologias</text>
  <rect x="24" y="{BAR_Y}" width="{WIDTH - 48}" height="{BAR_HEIGHT}" rx="5" fill="#161b22"/>
  {build_bar(shown)}
{build_legend(shown)}
</svg>
"""


def main() -> None:
    stats = json.loads((DATA_DIR / "stats.json").read_text(encoding="utf-8"))
    out_path = ASSETS_DIR / "langs-card.svg"
    out_path.write_text(build_svg(stats["languages"]), encoding="utf-8")
    print(f"[render_langs_card] salvo em {out_path}")


if __name__ == "__main__":
    main()
