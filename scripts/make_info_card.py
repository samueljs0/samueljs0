"""Gera o info card estilo neofetch (SVG), com fade/slide staggered nas linhas."""
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

WIDTH = 490
BG = "#0d1117"
BORDER = "#30363d"
LABEL_COLOR = "#58a6ff"
VALUE_COLOR = "#c9d1d9"
TITLE_COLOR = "#9fb3c8"

ROWS = [
    ("role", "Full-Stack Software Developer"),
    ("experience", "+4 anos em soluções web & mobile"),
    ("location", "Jaguaribe, CE - Brasil"),
    ("focus", "APIs REST, automação RPA, cloud & pipelines de dados"),
    ("stack", "Python, Java, TS, Django, Spring Boot, React, AWS, Docker"),
    ("status", "Aberto a novos desafios remotos"),
]

LINE_HEIGHT = 34
START_Y = 90


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(value: str, max_chars: int = 38) -> list[str]:
    words = value.split(" ")
    lines, current = [], ""
    for w in words:
        candidate = f"{current} {w}".strip()
        if len(candidate) > max_chars:
            lines.append(current)
            current = w
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def build_svg() -> str:
    rows_svg = []
    y = START_Y
    delay = 0.0
    for label, value in ROWS:
        value_lines = wrap(value)
        begin = f"{delay:.2f}s"
        rows_svg.append(f"""
  <g class="row" transform="translate(24,{y})" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{begin}" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" from="-16,{y}" to="24,{y}"
      dur="0.5s" begin="{begin}" fill="freeze"/>
    <text class="label" x="0" y="0">{escape(label)}</text>
    <text class="value" x="120" y="0">{escape(value_lines[0])}</text>
  </g>""")
        y += LINE_HEIGHT
        for extra in value_lines[1:]:
            rows_svg.append(f"""
  <g class="row" transform="translate(24,{y})" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{begin}" fill="freeze"/>
    <text class="value" x="120" y="0">{escape(extra)}</text>
  </g>""")
            y += LINE_HEIGHT
        delay += 0.18

    height = y - LINE_HEIGHT + 40
    rows_joined = "".join(rows_svg)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <style>
    .title {{ font: 700 16px 'Courier New', monospace; fill: {TITLE_COLOR}; }}
    .prompt {{ font: 400 13px 'Courier New', monospace; fill: #6e7681; }}
    .label {{ font: 700 13px 'Courier New', monospace; fill: {LABEL_COLOR}; }}
    .value {{ font: 400 13px 'Courier New', monospace; fill: {VALUE_COLOR}; }}
  </style>
  <rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <text class="prompt" x="24" y="34">samuel@github:~$</text>
  <text class="title" x="24" y="60">whoami</text>
{rows_joined}
</svg>
"""


def main() -> None:
    out_path = ASSETS_DIR / "info-card.svg"
    out_path.write_text(build_svg(), encoding="utf-8")
    print(f"[make_info_card] salvo em {out_path}")


if __name__ == "__main__":
    main()
