from __future__ import annotations

import html
import os
from pathlib import Path

from config import BG, BG2, BLUE, CYAN, FG, FRAME, GREEN, INFO_CARD_SVG, INFO_CARD_WIDTH, MUTED, ORANGE, USERNAME

ROWS = [
    ("host",),
    ("kv", "Now", "Software Engineer · Saigon, VN"),
    ("kv", "Work", "Full-stack web products"),
    ("kv", "Stack", "TypeScript · React · Node.js"),
    ("kv", "Focus", "Clean UI · APIs · performance"),
    ("gap",),
    ("sec", "Links"),
    ("kv", "Web", "luc.works"),
    ("kv", "Mail", "tanlucdev@gmail.com"),
    ("gap",),
    ("sec", "Also"),
    ("bul", "Photography, reading, running"),
    ("bul", "Lifting weights and building side projects"),
]


def main() -> None:
    frozen = os.getenv("STATIC") == "1"
    width, height, pad, titlebar_h = INFO_CARD_WIDTH, 490, 20, 30
    key_x, val_x, line_h = pad, pad + 92, 20.5
    rows = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Tan Luc profile card" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<defs><linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="12" fill="url(#ibg)"/>',
        f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{titlebar_h}" x2="{width}" y2="{titlebar_h}" stroke="{FRAME}"/>',
    ]
    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        rows.append(f'<circle cx="{pad + i*16}" cy="{titlebar_h/2}" r="5" fill="{dot}"/>')
    rows.append(f'<text x="{width/2}" y="{titlebar_h/2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">{USERNAME}@github: ~$ neofetch</text>')

    def rise(inner: str, i: int) -> str:
        if frozen:
            return f"<g>{inner}</g>"
        delay = 0.15 + i * 0.06
        return f'<g opacity="0" transform="translate(0,5)">{inner}<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/><animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>'

    y = titlebar_h + 30
    for i, row in enumerate(ROWS):
        kind = row[0]
        if kind == "gap":
            y += line_h * 0.5
            continue
        if kind == "host":
            inner = f'<text x="{key_x}" y="{y:.1f}" font-size="14" font-weight="700"><tspan fill="{GREEN}">tanlucdev</tspan><tspan fill="{MUTED}">@</tspan><tspan fill="{CYAN}">github</tspan></text><line x1="{key_x+126}" y1="{y-4:.1f}" x2="{width-pad}" y2="{y-4:.1f}" stroke="{FRAME}" stroke-opacity="0.8"/>'
        elif kind == "sec":
            title = html.escape(row[1])
            inner = f'<text x="{key_x}" y="{y:.1f}" fill="{BLUE}" font-size="12.5" font-weight="700">&#8212; {title}</text><line x1="{key_x + 12 + len(row[1])*8}" y1="{y-4:.1f}" x2="{width-pad}" y2="{y-4:.1f}" stroke="{FRAME}" stroke-opacity="0.8"/>'
        elif kind == "kv":
            inner = f'<text x="{key_x}" y="{y:.1f}" fill="{ORANGE}" font-size="12.5" font-weight="700">{html.escape(row[1])}</text><text x="{val_x}" y="{y:.1f}" fill="{FG}" font-size="12.5">{html.escape(row[2])}</text>'
        else:
            inner = f'<circle cx="{key_x+3}" cy="{y-4:.1f}" r="2.5" fill="{GREEN}"/><text x="{key_x+14}" y="{y:.1f}" fill="{FG}" font-size="12.5">{html.escape(row[1])}</text>'
        rows.append(rise(inner, i))
        y += line_h
    rows.append("</svg>")
    Path(INFO_CARD_SVG).write_text("".join(rows), encoding="utf-8")
    print(INFO_CARD_SVG)


if __name__ == "__main__":
    main()
