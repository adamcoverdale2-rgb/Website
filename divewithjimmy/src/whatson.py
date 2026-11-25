#!/usr/bin/env python3
"""Fetches Dive With Jimmy's upcoming sessions from their SSI / Scubago
calendar and saves them to src/events.json for build.py.

Run before building to refresh the dates:
    python3 src/whatson.py && python3 src/build.py
"""
import html
import json
import re
import urllib.request
from datetime import date, timedelta
from pathlib import Path

CENTER = "744483"  # Dive With Jimmy's SSI / Scubago centre ID
OUT = Path(__file__).resolve().parent / "events.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; site-builder)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def feed_url(start, end, page=1):
    return (f"https://my.divessi.com/extern/events/{CENTER}/view,overview,mode,list,theme,default,"
            f"category,all,search,,program,,dateId,0,allowFullscreen,true,page,{page},perPage,100,"
            f"startDate,{start},endDate,{end},language,eng")


def clean(t):
    t = html.unescape(html.unescape(re.sub(r"<[^>]+>", " ", t)))
    return re.sub(r"\s+", " ", t).strip()


def main():
    start = date.today()
    end = start + timedelta(days=730)
    events, page = [], 1
    while True:
        s = get(feed_url(start, end, page))
        offers = json.loads(re.search(r"var offerUrls = (\{.*?\})", s).group(1) or "{}") if "var offerUrls" in s else {}
        for group in re.split(r'<section data-type="event_group">', s)[1:]:
            ym = re.search(r"<h2>(\d{4}) - (\w+)</h2>", group)
            for m in re.finditer(r'data-type="event-item" data-category="([^"]*)" data-program="([^"]*)">.*?eventDetails\((\d+),\s*(\d+)\).*?<div class="date-indicator">\s*<h3>(\d+)</h3>\s*<h4>(\w+)</h4>.*?<div class="date-text">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', group, re.S):
                cat, prog, eid, did, day, month, title, desc = m.groups()
                events.append({"category": cat, "program": prog, "event_id": eid, "date_id": did,
                               "day": int(day), "month": month, "year": int(ym.group(1)) if ym else None,
                               "title": clean(title), "summary": clean(desc),
                               "url": (offers.get(eid, f"https://www.scubago.com/center/{CENTER}") + (f"?date_id={did}" if eid in offers else ""))})
        if f"page,{page + 1}," not in s or page > 10:
            break
        page += 1

    # The calendar gives each session's date; the Scubago offer page adds the
    # price and, for multi-day courses, the end date.
    from datetime import datetime
    for ev in events:
        ev["start"] = ev["end"] = datetime.strptime(f'{ev["day"]} {ev["month"]} {ev["year"]}', "%d %B %Y").date().isoformat()
        try:
            o = get(ev["url"])
            ld = re.search(r'"@type":"Event".*?"startDate":"([\d-]+)".*?"endDate":"([\d-]+)"', o, re.S)
            pr = re.search(r'"price":([\d.]+)', o)
            if ld and ld.group(1) == ev["start"]:
                ev["end"] = ld.group(2)
            if pr:
                ev["price"] = float(pr.group(1))
        except Exception as ex:  # keep the session even if its offer page fails
            print("offer page failed:", ev["title"], ex)

    events.sort(key=lambda e: (e.get("start", ""), e["title"]))
    OUT.write_text(json.dumps({"fetched": date.today().isoformat(), "center": CENTER,
                               "calendar": f"https://www.scubago.com/center/{CENTER}",
                               "events": events}, indent=1, ensure_ascii=False))
    print(f"Saved {len(events)} sessions to {OUT}")
    for ev in events:
        print(f'  {ev.get("start")}  {ev["title"]}  £{ev.get("price", "?")}')


if __name__ == "__main__":
    main()
