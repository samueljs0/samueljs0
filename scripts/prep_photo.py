"""Prepara a foto de origem: remove fundo e aumenta contraste (CLAHE)."""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def remove_background(img: Image.Image) -> Image.Image:
    try:
        from rembg import remove
        return remove(img)
    except Exception as exc:
        print(f"[prep_photo] rembg indisponível ({exc}); mantendo fundo original.")
        return img.convert("RGBA")


def boost_contrast(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    arr = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(arr)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    arr = cv2.merge((l, a, b))
    rgb = cv2.cvtColor(arr, cv2.COLOR_LAB2RGB)
    return Image.fromarray(rgb)


def main(source_path: str) -> None:
    src = Image.open(source_path)
    no_bg = remove_background(src)
    contrasted = boost_contrast(no_bg)

    if no_bg.mode == "RGBA":
        contrasted = contrasted.convert("RGBA")
        contrasted.putalpha(no_bg.split()[-1])

    out_path = DATA_DIR / "photo-prepped.png"
    contrasted.save(out_path)
    print(f"[prep_photo] salvo em {out_path}")


if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else str(DATA_DIR / "avatar.png")
    main(source)
