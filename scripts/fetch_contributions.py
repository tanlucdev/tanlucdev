from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from datetime import date, timedelta

import requests

from config import CONTRIB_JSON, HEATMAP_DAYS, HEATMAP_WEEKS, USERNAME

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""


def streak(days: list[dict], longest: bool) -> int:
    best = cur = 0
    today = date.today().isoformat()
    for item in sorted(days, key=lambda x: x["date"]):
        if item["count"] > 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
        if not longest and item["date"] == today:
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
    token = os.environ["GITHUB_TOKEN"]
    end = date.today()
    start = end - timedelta(days=HEATMAP_WEEKS * HEATMAP_DAYS - 1)
    payload = {"query": QUERY, "variables": {"login": USERNAME, "from": f"{start}T00:00:00Z", "to": f"{end}T23:59:59Z"}}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            res = requests.post("https://api.github.com/graphql", json=payload, headers=headers, timeout=20)
            res.raise_for_status()
            body = res.json()
            if body.get("errors"):
                raise RuntimeError(body["errors"])
            weeks = body["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            days = [
                {"date": day["date"], "count": int(day["contributionCount"])}
                for week in weeks
                for day in week["contributionDays"]
            ][-HEATMAP_WEEKS * HEATMAP_DAYS :]
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
        return 0
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
