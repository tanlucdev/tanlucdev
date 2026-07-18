from __future__ import annotations

import os
from pathlib import Path

from config import BG, FG, GREEN, INFO_CARD_SVG, INFO_CARD_WIDTH, MUTED, USERNAME

LINES = [
    ("user", USERNAME),
    ("now", "Software Engineer · Saigon, Vietnam"),
    ("prev", "Shipping web products"),
    ("stack", "TypeScript · React · Node.js"),
    ("highlights", "Practical UI · APIs · performance"),
    ("contact", "tanlucdev@gmail.com · luc.works"),
]


def main() -> None:
    frozen = os.getenv("STATIC") == "1"
    rows = []
    for i, (label, value) in enumerate(LINES):
        opacity = "1" if frozen else "0"
        anim = "" if frozen else f'<animate attributeName="opacity" from="0" to="1" dur="0.18s" begin="{0.2 + i * 0.18:.2f}s" fill="freeze"/>'
        y = 78 + i * 48
        rows.append(
            f'<g opacity="{opacity}">{anim}<text x="34" y="{y}" fill="{GREEN}">{label:<10}</text>'
            f'<text x="146" y="{y}" fill="{FG}">{value}</text></g>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{INFO_CARD_WIDTH}" height="520" viewBox="0 0 {INFO_CARD_WIDTH} 520" role="img" aria-label="Neofetch profile card">
<title>Neofetch profile card</title>
<path d="M0 0h{INFO_CARD_WIDTH}v520H0z" fill="{BG}"/>
<text x="34" y="38" fill="{MUTED}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="17">tanlucdev@github</text>
<path d="M34 52h420" stroke="{MUTED}" stroke-width="1"/>
<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="16">
{chr(10).join(rows)}
</g>
</svg>
'''
    Path(INFO_CARD_SVG).write_text(svg, encoding="utf-8")
    print(INFO_CARD_SVG)


if __name__ == "__main__":
    main()
