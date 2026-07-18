from __future__ import annotations

import argparse
import html
import os
from pathlib import Path

from config import ASCII_COLS, ASCII_RAMP, ASCII_ROWS, ASCII_SVG, BG, BG2, FRAME, INK, MUTED, SOURCE_PREPPED, USERNAME


def image_to_rows(path: Path) -> list[str]:
    from PIL import Image, ImageEnhance

    image = Image.open(path).convert("L")
    image = ImageEnhance.Brightness(image).enhance(1.02)
    image = ImageEnhance.Contrast(image).enhance(1.12)
    image = image.resize((ASCII_COLS, ASCII_ROWS), Image.Resampling.LANCZOS)
    chars = []
    ramp = ASCII_RAMP
    for y in range(ASCII_ROWS):
        row = ""
        for x in range(ASCII_COLS):
            lum = (image.getpixel((x, y)) / 255.0) ** 1.14
            row += " " if lum >= 0.82 else ramp[max(0, min(len(ramp) - 1, int((1 - lum) * (len(ramp) - 1) + 0.5)))]
        chars.append(row)
    return chars


def fallback_rows() -> list[str]:
    return [" " * ASCII_COLS for _ in range(ASCII_ROWS)]


def render(rows: list[str], out: Path) -> None:
    static = bool(os.getenv("STATIC"))
    cell_w, cell_h = 8, 15
    pad, titlebar_h, status_h = 20, 30, 30
    art_w, art_h = ASCII_COLS * cell_w, ASCII_ROWS * cell_h
    canvas_w, canvas_h = art_w + pad * 2, titlebar_h + art_h + status_h + pad
    art_top = titlebar_h + pad * 0.35
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" role="img" aria-label="Tan Luc ASCII portrait" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{FRAME}"/>',
    ]
    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{pad + i * 16}" cy="{titlebar_h / 2}" r="5" fill="{dot}"/>')
    parts.append(f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">{USERNAME}@github: ~$ ./portrait.sh</text>')
    for ry, row in enumerate(rows):
        y = art_top + ry * cell_h + cell_h * 0.74
        row_y = art_top + ry * cell_h
        delay = ry * 0.11
        text = f'<text xml:space="preserve" x="{pad}" y="{y:.1f}" fill="{INK}" font-size="{cell_h * 0.86:.1f}" textLength="{art_w}" lengthAdjust="spacing">{html.escape(row)}</text>'
        if static:
            parts.append(text)
        else:
            parts.append(f'<clipPath id="r{ry}"><rect x="{pad}" y="{row_y:.1f}" height="{cell_h}" width="0"><animate attributeName="width" from="0" to="{art_w}" begin="{delay:.3f}s" dur="0.11s" fill="freeze"/></rect></clipPath>')
            parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
            parts.append(f'<rect y="{row_y+1:.1f}" width="{cell_w}" height="{cell_h-2}" fill="{INK}" opacity="0"><animate attributeName="x" from="{pad}" to="{pad+art_w}" begin="{delay:.3f}s" dur="0.11s" fill="freeze"/><set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/><set attributeName="opacity" to="0" begin="{delay+0.11:.3f}s"/></rect>')
    status_y = titlebar_h + art_h + pad * 0.35
    parts.append(f'<line x1="0" y1="{status_y:.1f}" x2="{canvas_w}" y2="{status_y:.1f}" stroke="{FRAME}"/>')
    parts.append(f'<text x="{pad}" y="{status_y + 19:.1f}" fill="{MUTED}" font-size="13">{USERNAME}@github:~$ whoami <tspan fill="{INK}">Tan Luc</tspan></text>')
    parts.append(f'<rect x="{pad+217}" y="{status_y+7:.1f}" width="8" height="14" fill="{INK}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect></svg>')
    svg = "".join(parts)
    out.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=SOURCE_PREPPED)
    parser.add_argument("-o", "--output", type=Path, default=ASCII_SVG)
    args = parser.parse_args()
    render(image_to_rows(args.image) if args.image else fallback_rows(), args.output)
    print(args.output)


if __name__ == "__main__":
    main()
