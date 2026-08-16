from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

from config import CONTRIB_JSON, HEATMAP_DAYS, HEATMAP_WEEKS, USERNAME

DAY_RE = re.compile(r'data-date="(\d{4}-\d{2}-\d{2})".*?</td>\s*<tool-tip[^>]*>(.*?)</tool-tip>', re.S)


def streak(days: list[dict], longest: bool) -> int:
    best = cur = 0
    current_end = max((item["date"] for item in days), default="")
    for item in sorted(days, key=lambda x: x["date"]):
        if item["count"] > 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
        if not longest and item["date"] == current_end:
            return cur
    return best if longest else cur


def stats(days: list[dict]) -> dict:
    months: dict[str, int] = defaultdict(int)
    for item in days:
        months[item["date"][:7]] += item["count"]
    best = max(days, key=lambda x: (x["count"], x["date"]), default={"date": "", "count": 0})
    return {
        "total": sum(item["count"] for item in days),
        "current_streak": streak(days, False),
        "longest_streak": streak(days, True),
        "best_day": best,
        "monthly_totals": dict(sorted(months.items())),
    }


def fetch() -> dict:
    tz = ZoneInfo(os.getenv("PROFILE_TZ", "Asia/Ho_Chi_Minh"))
    end = datetime.now(tz).date()
    start = end - timedelta(days=HEATMAP_WEEKS * HEATMAP_DAYS - 1)
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            days_by_date = {}
            for year in range(start.year, end.year + 1):
                res = requests.get(f"https://github.com/users/{USERNAME}/contributions?from={year}-01-01&to={year}-12-31", timeout=20)
                res.raise_for_status()
                for day, label in DAY_RE.findall(res.text):
                    count = 0 if label.startswith("No ") else int(re.match(r"\d+", label).group())
                    if start.isoformat() <= day <= end.isoformat():
                        days_by_date[day] = count
            days = [{"date": day, "count": days_by_date[day]} for day in sorted(days_by_date)]
            if len(days) != HEATMAP_WEEKS * HEATMAP_DAYS:
                raise RuntimeError(f"expected 371 days, got {len(days)}")
            return {"username": USERNAME, "generated_at": end.isoformat(), "days": days, "stats": stats(days)}
        except Exception as exc:
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError(last_error)


def main() -> int:
    try:
        new = fetch()
    except Exception as exc:
        print(f"fetch failed; leaving existing JSON untouched: {exc}", file=sys.stderr)
        return 1
    old = json.loads(CONTRIB_JSON.read_text(encoding="utf-8")) if CONTRIB_JSON.exists() else None
    if old == new:
        print("contributions unchanged")
        return 0
    CONTRIB_JSON.parent.mkdir(parents=True, exist_ok=True)
    CONTRIB_JSON.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(CONTRIB_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
