"""Gera o card de competências (soft skills), estilo neofetch, largura cheia (860px)."""
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

WIDTH = 860
BG = "#0d1117"
BORDER = "#30363d"
TITLE_COLOR = "#9fb3c8"
HEADING_COLOR = "#58a6ff"
BODY_COLOR = "#c9d1d9"

COLS = 2
COL_WIDTH = (WIDTH - 48) / COLS
ROW_HEIGHT = 52
ROWS_START_Y = 84

ITEMS = [
    ("Mentoria técnica", "Apoio e orientação a devs juniores em revisão de código e boas práticas."),
    ("Autonomia ponta a ponta", "Conduz soluções da concepção ao deploy, sem supervisão direta."),
    ("Resolução analítica de problemas", "Automações que já reduziram 20% do tempo de processos operacionais."),
    ("Levantamento de requisitos", "Atua direto com as áreas de negócio na definição de soluções técnicas."),
    ("Colaboração multidisciplinar", "Integração entre frontend, backend e infraestrutura em times pequenos."),
    ("Trabalho remoto autogerenciado", "Rotina 100% remota desde 2024, em mais de um projeto simultâneo."),
]


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(value: str, max_chars: int = 44) -> list[str]:
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


def build_items() -> str:
    rows = []
    delay = 0.0
    for i, (heading, body) in enumerate(ITEMS):
        col = i % COLS
        row = i // COLS
        x = 24 + col * COL_WIDTH
        y = ROWS_START_Y + row * ROW_HEIGHT
        begin = f"{delay:.2f}s"
        body_lines = wrap(body)
        body_svg = "".join(
            f'<text class="body" x="0" y="{18 + j * 16}">{escape(line)}</text>'
            for j, line in enumerate(body_lines)
        )
        rows.append(f"""
  <g transform="translate({x:.1f},{y})" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{begin}" fill="freeze"/>
    <text class="heading">▸ {escape(heading)}</text>
    {body_svg}
  </g>""")
        delay += 0.12
    return "".join(rows)


def build_svg() -> str:
    n_rows = -(-len(ITEMS) // COLS)
    height = ROWS_START_Y + n_rows * ROW_HEIGHT + 8

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <style>
    .title {{ font: 700 18px 'Courier New', monospace; fill: {TITLE_COLOR}; }}
    .prompt {{ font: 400 14px 'Courier New', monospace; fill: #6e7681; }}
    .heading {{ font: 700 14px 'Courier New', monospace; fill: {HEADING_COLOR}; }}
    .body {{ font: 400 13px 'Courier New', monospace; fill: {BODY_COLOR}; }}
  </style>
  <rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <text class="prompt" x="24" y="34">samuel@github:~$</text>
  <text class="title" x="24" y="60">competencias</text>
{build_items()}
</svg>
"""


def main() -> None:
    out_path = ASSETS_DIR / "competencias-card.svg"
    out_path.write_text(build_svg(), encoding="utf-8")
    print(f"[make_competencias_card] salvo em {out_path}")


if __name__ == "__main__":
    main()
