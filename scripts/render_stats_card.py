"""Gera o card 'Estatísticas do GitHub' (SVG) no padrão github-readme-stats:
título com o nome, ícones por linha e um anel de nota à direita.

A nota (S/A+/A/.../C) é um cálculo PRÓPRIO e simplificado (log-escala + pesos
arbitrários), não a fórmula real do github-readme-stats — serve só para dar o
mesmo efeito visual do anel, sem inventar o número deles."""
import json
import math
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

WIDTH = 430
BG = "#0d1117"
BORDER = "#30363d"
TITLE_COLOR = "#c9d1d9"
LABEL_COLOR = "#8b949e"
VALUE_COLOR = "#c9d1d9"
RING_BG = "#30363d"

ROW_Y_START = 76
ROW_HEIGHT = 27
RING_CX = WIDTH - 58
RING_R = 34

# (label, data_key, ícone, cor)
ROWS = [
    ("Total de estrelas", "stars", "star", "#e3b341"),
    ("Total de commits", "commits", "commit", "#39d0d8"),
    ("Total de PRs", "prs", "pr", "#a371f7"),
    ("Total de issues", "issues", "issue", "#f85149"),
    ("Contribuiu p/ (ano passado)", "contributed_repos", "repo", "#3fb950"),
]

# (limiar de score 0-1, letra, cor do anel)
GRADES = [
    (0.90, "S", "#3fb950"),
    (0.80, "A+", "#3fb950"),
    (0.70, "A", "#3fb950"),
    (0.60, "A-", "#3fb950"),
    (0.50, "B+", "#39d0d8"),
    (0.40, "B", "#39d0d8"),
    (0.30, "B-", "#39d0d8"),
    (0.20, "C+", "#e3b341"),
    (0.00, "C", "#e3b341"),
]

# peso e "teto" de referência (log-escala) de cada métrica
WEIGHTS = {
    "commits": (0.40, 1000),
    "prs": (0.20, 200),
    "issues": (0.10, 100),
    "stars": (0.15, 200),
    "contributed_repos": (0.15, 20),
}


def score(stats: dict) -> float:
    total = 0.0
    for key, (weight, ceiling) in WEIGHTS.items():
        normalized = math.log1p(stats[key]) / math.log1p(ceiling)
        total += weight * min(normalized, 1.0)
    return min(total, 1.0)


def grade_for(s: float) -> tuple[str, str]:
    for threshold, letter, color in GRADES:
        if s >= threshold:
            return letter, color
    return GRADES[-1][1], GRADES[-1][2]


def icon(kind: str, color: str) -> str:
    if kind == "star":
        pts = []
        for i in range(10):
            r = 6 if i % 2 == 0 else 2.6
            a = math.pi / 2 + i * math.pi / 5
            pts.append(f"{r * math.cos(a):.2f},{-r * math.sin(a):.2f}")
        return f'<polygon points="{" ".join(pts)}" fill="{color}"/>'
    if kind == "commit":
        return (
            f'<line x1="-7" y1="0" x2="-3" y2="0" stroke="{color}" stroke-width="2"/>'
            f'<circle r="3" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<line x1="3" y1="0" x2="7" y2="0" stroke="{color}" stroke-width="2"/>'
        )
    if kind == "pr":
        return (
            f'<line x1="0" y1="-6" x2="0" y2="6" stroke="{color}" stroke-width="2"/>'
            f'<circle cy="-6" r="2.6" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<circle cy="6" r="2.6" fill="{color}"/>'
        )
    if kind == "issue":
        return (
            f'<circle r="6" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<circle r="1.8" fill="{color}"/>'
        )
    if kind == "repo":
        return (
            f'<rect x="-6" y="-6" width="12" height="12" rx="2" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<line x1="-6" y1="-1.5" x2="6" y2="-1.5" stroke="{color}" stroke-width="1.5"/>'
        )
    return ""


def build_rows(stats: dict) -> str:
    rows_svg = []
    y = ROW_Y_START
    delay = 0.0
    for label, key, kind, color in ROWS:
        value = stats[key]
        begin = f"{delay:.2f}s"
        rows_svg.append(f"""
  <g class="row" transform="translate(24,{y})" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{begin}" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" from="4,{y}" to="24,{y}"
      dur="0.5s" begin="{begin}" fill="freeze"/>
    <g transform="translate(6,-4)">{icon(kind, color)}</g>
    <text class="label" x="20" y="0">{label}:</text>
    <text class="value" x="268" y="0">{value}</text>
  </g>""")
        y += ROW_HEIGHT
        delay += 0.15
    return "".join(rows_svg)


def build_ring(cy: float, s: float, letter: str, color: str) -> str:
    circumference = 2 * math.pi * RING_R
    filled = circumference * s
    return f"""
  <circle cx="{RING_CX}" cy="{cy}" r="{RING_R}" fill="none" stroke="{RING_BG}" stroke-width="6"/>
  <circle cx="{RING_CX}" cy="{cy}" r="{RING_R}" fill="none" stroke="{color}" stroke-width="6"
    stroke-linecap="round" stroke-dasharray="{filled:.2f} {circumference:.2f}"
    transform="rotate(-90 {RING_CX} {cy})">
    <animate attributeName="stroke-dasharray" from="0 {circumference:.2f}" to="{filled:.2f} {circumference:.2f}"
      dur="1s" begin="0.2s" fill="freeze"/>
  </circle>
  <text class="grade" x="{RING_CX}" y="{cy + 8}" text-anchor="middle" fill="{color}">{letter}</text>"""


def build_svg(stats: dict) -> str:
    height = ROW_Y_START + len(ROWS) * ROW_HEIGHT - ROW_HEIGHT + 40
    ring_cy = (ROW_Y_START + (ROW_Y_START + (len(ROWS) - 1) * ROW_HEIGHT)) / 2
    s = score(stats)
    letter, color = grade_for(s)

    title = f"Estatísticas do GitHub de {stats['name']}"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <style>
    .title {{ font: 700 15px 'Courier New', monospace; fill: {TITLE_COLOR}; }}
    .label {{ font: 400 13px 'Courier New', monospace; fill: {LABEL_COLOR}; }}
    .value {{ font: 700 13px 'Courier New', monospace; fill: {VALUE_COLOR}; }}
    .grade {{ font: 700 26px 'Courier New', monospace; }}
  </style>
  <rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <text class="title" x="24" y="34">{title}</text>
{build_rows(stats)}
{build_ring(ring_cy, s, letter, color)}
</svg>
"""


def main() -> None:
    stats = json.loads((DATA_DIR / "stats.json").read_text(encoding="utf-8"))
    out_path = ASSETS_DIR / "stats-card.svg"
    out_path.write_text(build_svg(stats), encoding="utf-8")
    print(f"[render_stats_card] salvo em {out_path}")


if __name__ == "__main__":
    main()
