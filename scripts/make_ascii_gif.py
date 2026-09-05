from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import ASCII_COLS, ASCII_ROWS, ASCII_GIF, BG, BG2, FRAME, INK, MUTED, SOURCE_PREPPED, USERNAME
from make_ascii_svg import balance_rows, fallback_rows, image_to_rows


def font() -> ImageFont.FreeTypeFont:
    for path in (
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, 13)
    return ImageFont.load_default()


def render(rows: list[str], out: Path) -> None:
    cell_w, cell_h = 8, 15
    pad, titlebar_h = 20, 30
    art_w, art_h = ASCII_COLS * cell_w, ASCII_ROWS * cell_h
    canvas_w, canvas_h = art_w + pad * 2, titlebar_h + art_h + 30 + pad
    art_top = titlebar_h + pad * 0.35
    frame_ms = 110
    font_ = font()
    frames = []
    for step in range(ASCII_ROWS + 1):
        img = Image.new("RGBA", (canvas_w, canvas_h), BG)
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, canvas_w - 1, canvas_h - 1), outline=FRAME, width=1)
        draw.rectangle((0, 0, canvas_w, titlebar_h), fill=BG2)
        draw.line((0, titlebar_h, canvas_w, titlebar_h), fill=FRAME)
        for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            x = pad + i * 16
            draw.ellipse((x - 5, 15 - 5, x + 5, 15 + 5), fill=dot)
        draw.text((canvas_w / 2, 11), f"{USERNAME}@github: ~$ ./portrait.sh", fill=MUTED, anchor="ma", font=font_)
        for ry, row in enumerate(rows):
            delay = ry * 0.11
            progress = max(0.0, min(1.0, (step * frame_ms / 1000 - delay) / 0.11))
            if progress <= 0:
                continue
            row_y = art_top + ry * cell_h
            clip_w = max(1, int(art_w * progress))
            layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            layer_draw = ImageDraw.Draw(layer)
            layer_draw.text((pad, row_y + 2), row, fill=INK, font=font_)
            mask = Image.new("L", (canvas_w, canvas_h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rectangle((pad, row_y, pad + clip_w, row_y + cell_h), fill=255)
            img = Image.composite(layer, img, mask)
            if progress < 1:
                cursor_x = min(pad + clip_w, pad + art_w - cell_w)
                draw = ImageDraw.Draw(img)
                draw.rectangle((cursor_x, row_y + 1, cursor_x + cell_w, row_y + cell_h - 1), fill=INK)
        status_y = titlebar_h + art_h + pad * 0.35
        draw.line((0, status_y, canvas_w, status_y), fill=FRAME)
        draw.text((pad, status_y + 19), f"{USERNAME}@github:~$ whoami ", fill=MUTED, font=font_)
        draw.text((pad + 217, status_y + 19), "Tan Luc", fill=INK, font=font_)
        frames.append(img.convert("P", palette=Image.Palette.ADAPTIVE))
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=frame_ms,
        loop=0,
        optimize=False,
        disposal=2,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=SOURCE_PREPPED)
    parser.add_argument("-o", "--output", type=Path, default=ASCII_GIF)
    args = parser.parse_args()
    render(balance_rows(image_to_rows(args.image) if args.image else fallback_rows()), args.output)
    print(args.output)


if __name__ == "__main__":
    main()
