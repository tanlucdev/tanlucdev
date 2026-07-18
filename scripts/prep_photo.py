from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a portrait for ASCII rendering.")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("data/portrait-prepped.png"))
    args = parser.parse_args()

    image = Image.open(args.input).convert("RGBA")
    try:
        from rembg import remove

        image = remove(image)
    except Exception as exc:
        print(f"rembg skipped: {exc}")

    white = Image.new("RGBA", image.size, "white")
    image = Image.alpha_composite(white, image).convert("L")
    try:
        import cv2
        import numpy as np

        arr = np.array(image)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        out = Image.fromarray(clahe.apply(arr))
    except Exception as exc:
        from PIL import ImageEnhance, ImageOps

        print(f"CLAHE skipped: {exc}")
        out = ImageOps.autocontrast(image, cutoff=1)
        out = ImageEnhance.Contrast(out).enhance(1.35)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
