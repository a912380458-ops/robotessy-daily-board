#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Asia/Shanghai")
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "data" / "latest.json"
KEYWORD = os.getenv("KEYWORD", "Robotessy")
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "14"))
MAX_ITEMS_PER_DAY = int(os.getenv("MAX_ITEMS_PER_DAY", "8"))
USER_AGENT = "Mozilla/5.0 (compatible; RobotessyDigestBot/1.0)"


def google_news_rss(query: str, hl: str, gl: str, ceid: str) -> str:
    encoded = urllib.parse.quote_plus(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl={hl}&gl={gl}&ceid={ceid}"


def parse_pub_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def fetch_items(url: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()

    root = ET.fromstring(raw)
    items = []
    for node in root.findall("./channel/item"):
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        pub_date = parse_pub_date((node.findtext("pubDate") or "").strip())
        source = (node.findtext("source") or "").strip()
        if not title or not link or not pub_date:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "source": source,
                "published_at": pub_date.astimezone(TIMEZONE).isoformat(),
            }
        )
    return items


def dedupe_and_group(items: list[dict], now: datetime) -> list[dict]:
    seen = set()
    filtered = []
    cutoff = now - timedelta(days=LOOKBACK_DAYS)

    for item in sorted(items, key=lambda x: x["published_at"], reverse=True):
        dt = datetime.fromisoformat(item["published_at"])
        if dt < cutoff:
            continue
        key = (item["title"], dt.date().isoformat())
        if key in seen:
            continue
        seen.add(key)
        filtered.append(item)

    buckets: dict[str, list[dict]] = {}
    for item in filtered:
        day = item["published_at"][:10]
        buckets.setdefault(day, []).append(item)

    result = []
    for day in sorted(buckets.keys(), reverse=True):
        entries = buckets[day][:MAX_ITEMS_PER_DAY]
        result.append({"date": day, "total": len(buckets[day]), "items": entries})
    return result


def build_region(region: str) -> list[dict]:
    if region == "china":
        queries = [
            f'"{KEYWORD}" 中国',
            f'"{KEYWORD}" 自动驾驶 中国',
            f'"{KEYWORD}" Robotaxi 中国',
        ]
        params = ("zh-CN", "CN", "CN:zh-Hans")
    else:
        queries = [
            f'"{KEYWORD}"',
            f'"{KEYWORD}" robotaxi',
            f'"{KEYWORD}" autonomous driving',
        ]
        params = ("en-US", "US", "US:en")

    all_items: list[dict] = []
    for q in queries:
        url = google_news_rss(q, *params)
        try:
            all_items.extend(fetch_items(url))
        except Exception:
            continue

    now = datetime.now(TIMEZONE)
    return dedupe_and_group(all_items, now)


def main() -> None:
    now = datetime.now(TIMEZONE)
    data = {
        "updated_at": now.isoformat(),
        "timezone": "Asia/Shanghai",
        "keyword": KEYWORD,
        "china": build_region("china"),
        "overseas": build_region("overseas"),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"updated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
