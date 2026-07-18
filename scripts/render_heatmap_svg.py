from __future__ import annotations

import html
import json

from config import BG, CELL, CONTRIB_JSON, FG, GAP, GREEN, HEATMAP_DAYS, HEATMAP_PALETTE, HEATMAP_SVG, HEATMAP_WIDTH, HEATMAP_WEEKS, MUTED, RADIUS


def color(count: int, max_count: int) -> str:
    if count <= 0 or max_count <= 0:
        return HEATMAP_PALETTE[0]
    index = min(5, 1 + int(count / max_count * 4.999))
    return HEATMAP_PALETTE[index]


def main() -> None:
    data = json.loads(CONTRIB_JSON.read_text(encoding="utf-8"))
    days = data["days"][-HEATMAP_WEEKS * HEATMAP_DAYS :]
    max_count = max((d["count"] for d in days), default=0)
    cells = []
    for i, day in enumerate(days):
        week, weekday = divmod(i, HEATMAP_DAYS)
        x = 14 + week * (CELL + GAP)
        y = 54 + weekday * (CELL + GAP)
        delay = (week + weekday) * 0.018
        label = html.escape(f'{day["date"]}: {day["count"]} contributions')
        cells.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RADIUS}" fill="{color(day["count"], max_count)}" opacity="0" transform="translate(0 -8)">'
            f'<title>{label}</title><animate attributeName="opacity" from="0" to="1" dur="0.18s" begin="{delay:.3f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 -8" to="0 0" dur="0.18s" begin="{delay:.3f}s" fill="freeze"/></rect>'
        )
    total = data.get("stats", {}).get("total", sum(d["count"] for d in days))
    footer = html.escape(f"{total} contributions in the last year")
    legend = "Less -> More"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{HEATMAP_WIDTH}" height="190" viewBox="0 0 {HEATMAP_WIDTH} 190" role="img" aria-label="{footer}">
<title>{footer}</title>
<path d="M0 0h{HEATMAP_WIDTH}v190H0z" fill="{BG}"/>
<text x="14" y="28" fill="{FG}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="16">contributionCalendar</text>
<g>{chr(10).join(cells)}</g>
<text x="14" y="174" fill="{MUTED}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="13">{footer}</text>
<text x="744" y="174" fill="{GREEN}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="13">{legend}</text>
</svg>
'''
    HEATMAP_SVG.write_text(svg, encoding="utf-8")
    print(HEATMAP_SVG)


if __name__ == "__main__":
    main()
