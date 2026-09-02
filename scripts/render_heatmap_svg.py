"""Renderiza o grid de contribuições (53 semanas x 7 dias) como SVG animado."""
import json
from datetime import date, datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BOX, GAP = 11, 3
COLS, ROWS = 53, 7
MARGIN = 20


def load_days() -> list[dict]:
    path = DATA_DIR / "contributions.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def color_for(level: int) -> str:
    return PALETTE[min(max(level, 0), len(PALETTE) - 1)]


def build_svg(days: list[dict]) -> str:
    width = MARGIN * 2 + COLS * (BOX + GAP)
    height = MARGIN * 2 + ROWS * (BOX + GAP)

    by_date = {d["date"]: d for d in days}
    ordered_dates = sorted(by_date.keys())

    boxes = []
    if ordered_dates:
        first = datetime.strptime(ordered_dates[0], "%Y-%m-%d").date()
        for i, d_str in enumerate(ordered_dates):
            d = by_date[d_str]
            idx = i + ((first.isoweekday() % 7))
            col = idx // ROWS
            row = idx % ROWS
            x = MARGIN + col * (BOX + GAP)
            y = MARGIN + row * (BOX + GAP)
            delay = col * 0.015
            boxes.append(
                f'<rect x="{x}" y="-{BOX}" width="{BOX}" height="{BOX}" rx="2" '
                f'fill="{color_for(d["level"])}">'
                f'<animate attributeName="y" from="-{BOX}" to="{y}" dur="0.4s" '
                f'begin="{delay:.3f}s" fill="freeze" calcMode="spline" '
                f'keySplines="0.2 0.8 0.2 1"/>'
                f'</rect>'
            )

    boxes_joined = "\n  ".join(boxes)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#010409"/>
  {boxes_joined}
</svg>
"""


def main() -> None:
    days = load_days()
    svg = build_svg(days)
    out_path = ASSETS_DIR / "contrib-heatmap.svg"
    out_path.write_text(svg, encoding="utf-8")
    print(f"[render_heatmap_svg] {len(days)} dias -> {out_path}")


if __name__ == "__main__":
    main()
