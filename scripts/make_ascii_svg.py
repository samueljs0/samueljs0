"""Converte a foto preparada em um SVG de ASCII art com animação de wipe."""
from pathlib import Path

import numpy as np
from PIL import Image

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

COLS, ROWS = 100, 53
RAMP = " .`:-=+*cs#%@"
CHAR_W, CHAR_H = 7, 12
FONT_SIZE = 11
COLOR = "#9fb3c8"
BG = "#0d1117"


def load_grid(path: Path) -> np.ndarray:
    img = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", img.size, (13, 17, 23, 255))
    img = Image.alpha_composite(bg, img).convert("L")
    img = img.resize((COLS, ROWS))
    return np.asarray(img)


def brightness_to_char(v: int) -> str:
    idx = int((v / 255) * (len(RAMP) - 1))
    return RAMP[idx]


def build_svg(grid: np.ndarray) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    rows_svg = []
    for r in range(ROWS):
        chars = "".join(brightness_to_char(int(v)) for v in grid[r])
        chars = chars.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        y = (r + 1) * CHAR_H - 2
        begin = f"{r * 0.02:.2f}s"
        rows_svg.append(
            f'  <text x="0" y="{y}" class="row" opacity="0">{chars}'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" '
            f'begin="{begin}" fill="freeze"/></text>'
        )

    rows_joined = "\n".join(rows_svg)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    .row {{ font-family: 'Courier New', monospace; font-size: {FONT_SIZE}px; fill: {COLOR}; white-space: pre; }}
  </style>
  <rect width="{width}" height="{height}" fill="{BG}"/>
{rows_joined}
</svg>
"""


def main() -> None:
    prepped = DATA_DIR / "photo-prepped.png"
    source = prepped if prepped.exists() else DATA_DIR / "avatar.png"
    grid = load_grid(source)
    svg = build_svg(grid)
    out_path = ASSETS_DIR / "samuel-ascii.svg"
    out_path.write_text(svg, encoding="utf-8")
    print(f"[make_ascii_svg] salvo em {out_path}")


if __name__ == "__main__":
    main()
