from __future__ import annotations

import sys
import xml.etree.ElementTree as ET

from config import HEATMAP_DAYS, HEATMAP_SVG, HEATMAP_WEEKS


def main() -> int:
    if not HEATMAP_SVG.exists() or HEATMAP_SVG.stat().st_size == 0:
        print("heatmap SVG missing or empty", file=sys.stderr)
        return 1
    root = ET.parse(HEATMAP_SVG).getroot()
    rects = [el for el in root.iter() if el.tag.endswith("rect")]
    expected = HEATMAP_WEEKS * HEATMAP_DAYS
    if len(rects) != expected:
        print(f"expected {expected} rect cells, got {len(rects)}", file=sys.stderr)
        return 1
    print(f"ok: {len(rects)} cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
