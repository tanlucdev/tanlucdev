from __future__ import annotations

import html
import json
from datetime import date

from config import BG, BG2, CELL, CONTRIB_JSON, CYAN, FG, FRAME, GAP, GOLD, GREEN, HEATMAP_DAYS, HEATMAP_PALETTE, HEATMAP_SVG, HEATMAP_WIDTH, HEATMAP_WEEKS, MUTED, RADIUS, USERNAME


def color(count: int, max_count: int) -> str:
    if count <= 0 or max_count <= 0:
        return HEATMAP_PALETTE[0]
    index = min(5, 1 + int(count / max_count * 4.999))
    return HEATMAP_PALETTE[index]


def main() -> None:
    data = json.loads(CONTRIB_JSON.read_text(encoding="utf-8"))
    days = data["days"][-HEATMAP_WEEKS * HEATMAP_DAYS :]
    max_count = max((d["count"] for d in days), default=0)
    step = CELL + 3
    pad = 22
    label_w = 30
    titlebar_h = 30
    top_h = 20
    grid_left = pad + label_w
    grid_top = titlebar_h + top_h
    art_w = HEATMAP_WEEKS * step
    art_h = HEATMAP_DAYS * step
    width = pad + label_w + art_w + pad
    height = titlebar_h + top_h + art_h + 88 + pad
    cells = []
    for i, day in enumerate(days):
        week, weekday = divmod(i, HEATMAP_DAYS)
        x = grid_left + week * step
        y = grid_top + weekday * step
        delay = week * 0.018 + weekday * 0.045
        label = html.escape(f'{day["date"]}: {day["count"]} contributions')
        cells.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RADIUS}" fill="{color(day["count"], max_count)}" opacity="0" transform="translate(0 -6)">'
            f'<title>{label}</title><animate attributeName="opacity" from="0" to="1" dur="0.18s" begin="{delay:.3f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 -6" to="0 0" dur="0.18s" begin="{delay:.3f}s" fill="freeze"/></rect>'
        )
    total = data.get("stats", {}).get("total", sum(d["count"] for d in days))
    current = data.get("stats", {}).get("current_streak", 0)
    longest = data.get("stats", {}).get("longest_streak", 0)
    best = data.get("stats", {}).get("best_day", {"date": "", "count": 0})
    footer = html.escape(f"{total} contributions in the last year")
    months = []
    seen = set()
    for i, item in enumerate(days):
        d = date.fromisoformat(item["date"])
        if d.day <= 7 and (d.year, d.month) not in seen:
            seen.add((d.year, d.month))
            months.append(f'<text x="{grid_left + (i // 7) * step}" y="{titlebar_h + 14}" fill="{MUTED}" font-size="10">{d.strftime("%b")}</text>')
    labels = []
    for weekday, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        labels.append(f'<text x="{pad}" y="{grid_top + weekday * step + CELL * 0.78:.1f}" fill="{MUTED}" font-size="9">{name}</text>')
    legend_x = width - pad - 138
    legend_y = grid_top + art_h + 6
    legend = [f'<text x="{legend_x}" y="{legend_y + CELL * 0.8:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>']
    lx = legend_x + 8
    for c in HEATMAP_PALETTE:
        legend.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL-1}" height="{CELL-1}" rx="2.2" fill="{c}"/>')
        lx += CELL
    legend.append(f'<text x="{lx + 4}" y="{legend_y + CELL * 0.8:.1f}" fill="{MUTED}" font-size="10">More</text>')
    sep_y = legend_y + CELL + 14
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{HEATMAP_WIDTH}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{footer}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">
<title>{footer}</title>
<defs><linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>
<rect width="{width}" height="{height}" rx="12" fill="url(#hbg)"/>
<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{CYAN}" stroke-width="1" stroke-opacity="0.55"/>
<line x1="0" y1="{titlebar_h}" x2="{width}" y2="{titlebar_h}" stroke="{FRAME}" stroke-opacity="0.8"/>
<circle cx="{pad}" cy="{titlebar_h/2}" r="5" fill="#ff5f56"/><circle cx="{pad+16}" cy="{titlebar_h/2}" r="5" fill="#ffbd2e"/><circle cx="{pad+32}" cy="{titlebar_h/2}" r="5" fill="#27c93f"/>
<text x="{width/2}" y="{titlebar_h/2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">{USERNAME}@github: ~/contributions --graph</text>
{chr(10).join(months)}
{chr(10).join(labels)}
<g>{chr(10).join(cells)}</g>
{chr(10).join(legend)}
<line x1="0" y1="{sep_y}" x2="{width}" y2="{sep_y}" stroke="{FRAME}" stroke-opacity="0.35"/>
<text x="{pad}" y="{sep_y + 24}" fill="{GREEN}" font-size="13"><tspan font-weight="700">{total:,}</tspan><tspan fill="{MUTED}"> contributions in the last year</tspan></text>
<text x="{width-pad}" y="{sep_y + 24}" fill="{MUTED}" font-size="12" text-anchor="end">{days[0]["date"]} &#8594; {days[-1]["date"]}</text>
<text x="{pad}" y="{sep_y + 48}" fill="{MUTED}" font-size="13">current streak <tspan fill="{CYAN}" font-weight="700">{current} days</tspan><tspan fill="{MUTED}">   &#183;   longest </tspan><tspan fill="{CYAN}" font-weight="700">{longest} days</tspan></text>
<text x="{width-pad}" y="{sep_y + 48}" fill="{MUTED}" font-size="12" text-anchor="end">best day <tspan fill="{GOLD}" font-weight="700">{best.get("count", 0)}</tspan> on {html.escape(best.get("date") or "n/a")}</text>
</svg>
'''
    HEATMAP_SVG.write_text(svg, encoding="utf-8")
    print(HEATMAP_SVG)


if __name__ == "__main__":
    main()
