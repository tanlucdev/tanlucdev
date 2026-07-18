from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

TARGET_ASPECT = 100 / 53


def subject_box(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox:
        return bbox

    rgb = image.convert("RGB")
    px = rgb.load()
    xs, ys = [], []
    for y in range(rgb.height):
        for x in range(rgb.width):
            r, g, b = px[x, y]
            if min(r, g, b) < 245:
                xs.append(x)
                ys.append(y)
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1) if xs else (0, 0, image.width, image.height)


def crop_upper_subject(image: Image.Image) -> Image.Image:
    left, top, right, bottom = subject_box(image)
    width = right - left
    height = bottom - top
    crop_h = max(1, int(height * 0.46))
    crop_w = int(crop_h * TARGET_ASPECT)
    cx = (left + right) // 2
    cy = int(top + height * 0.26)
    x0 = cx - crop_w // 2
    y0 = cy - crop_h // 2
    x1 = x0 + crop_w
    y1 = y0 + crop_h

    canvas = Image.new("RGBA", (crop_w, crop_h), "white")
    src_x0, src_y0 = max(0, x0), max(0, y0)
    src_x1, src_y1 = min(image.width, x1), min(image.height, y1)
    patch = image.crop((src_x0, src_y0, src_x1, src_y1))
    canvas.paste(patch, (src_x0 - x0, src_y0 - y0), patch)
    return canvas


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

    image = crop_upper_subject(image)
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
