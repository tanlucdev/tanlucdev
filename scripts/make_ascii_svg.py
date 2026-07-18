from __future__ import annotations

import argparse
import html
import math
from pathlib import Path

from config import ASCII_COLS, ASCII_RAMP, ASCII_ROWS, ASCII_SVG, BG, FG, PORTRAIT_WIDTH


def image_to_rows(path: Path) -> list[str]:
    from PIL import Image

    image = Image.open(path).convert("L").resize((ASCII_COLS, ASCII_ROWS))
    chars = []
    ramp = ASCII_RAMP
    for y in range(ASCII_ROWS):
        row = ""
        for x in range(ASCII_COLS):
            value = image.getpixel((x, y))
            row += ramp[(255 - value) * (len(ramp) - 1) // 255]
        chars.append(row.rstrip() or " ")
    return chars


def fallback_rows() -> list[str]:
    ramp = ASCII_RAMP
    rows = []
    for y in range(ASCII_ROWS):
        line = ""
        ny = (y / (ASCII_ROWS - 1)) * 2 - 1
        for x in range(ASCII_COLS):
            nx = (x / (ASCII_COLS - 1)) * 2 - 1
            face = ((nx / 0.72) ** 2 + ((ny + 0.03) / 0.94) ** 2) < 1
            hair = ((nx / 0.78) ** 2 + ((ny + 0.42) / 0.45) ** 2) < 1 and ny < -0.18
            jaw = abs(nx) < 0.46 and 0.25 < ny < 0.72
            eyes = (abs(nx - 0.24) < 0.08 or abs(nx + 0.24) < 0.08) and -0.12 < ny < -0.03
            smile = abs(ny - (0.25 + 0.12 * math.cos(nx * 5))) < 0.025 and abs(nx) < 0.32
            mark = hair or (face and (jaw or eyes or smile or abs(nx) > 0.62))
            line += ramp[-1] if mark else ramp[0]
        rows.append(line.rstrip() or " ")
    return rows


def render(rows: list[str], out: Path) -> None:
    height = 520
    char_w = PORTRAIT_WIDTH / ASCII_COLS
    line_h = height / ASCII_ROWS
    lines = []
    for i, row in enumerate(rows):
        delay = i * 0.035
        lines.append(
            f'<text x="10" y="{24 + i * line_h:.2f}" opacity="0">{html.escape(row)}'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.01s" begin="{delay:.2f}s" fill="freeze"/></text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{PORTRAIT_WIDTH}" height="{height}" viewBox="0 0 {PORTRAIT_WIDTH} {height}" role="img" aria-label="ASCII portrait">
<title>ASCII portrait</title>
<path d="M0 0h{PORTRAIT_WIDTH}v{height}H0z" fill="{BG}"/>
<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{char_w * 1.88:.2f}" fill="{FG}" xml:space="preserve">
{chr(10).join(lines)}
</g>
</svg>
'''
    out.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=ASCII_SVG)
    args = parser.parse_args()
    render(image_to_rows(args.image) if args.image else fallback_rows(), args.output)
    print(args.output)


if __name__ == "__main__":
    main()
