"""St. Mary's Perivale (London) -- livestream schedule from the venue website.

The schedule page (``SCHEDULE_URL``) lists the whole season; each concert links
to a per-event detail page whose URL carries the full date
(``events-YYYY-MM-DD.shtml``) and whose body carries the start time
(e.g. "... 2 pm ..."). We collect upcoming detail links from the schedule, then
read the time from each detail page. St Mary's also streams to YouTube
(``st.mary`` in channels.json), so this is an early-visibility complement.
"""

from __future__ import annotations

import datetime as dt
import re

import pytz

from ..registry import register
from .base import PageScraper

BASE_URL = "https://www.st-marys-perivale.org.uk/"
SCHEDULE_URL = BASE_URL + "events-001.shtml"
YOUTUBE_URL = "https://www.youtube.com/@stmarysperivale2842"

# events-2026-09-08.shtml -> (2026, 09, 08)
DATE_IN_HREF = re.compile(r"events-(\d{4})-(\d{2})-(\d{2})\.shtml")
# "2 pm", "7.30 pm", "11:00 am"
TIME_RE = re.compile(r"\b(\d{1,2})(?:[.:](\d{2}))?\s*([ap]m)\b", re.IGNORECASE)


@register("stmary")
class StMaryScraper(PageScraper):
    def __init__(self):
        super().__init__(pytz.timezone("Europe/London"))

    def get_upcoming_livestreams(self) -> list[dict]:
        soup = self.get_soup(SCHEDULE_URL)
        today = dt.date.today()

        items: list[dict] = []
        seen: set[str] = set()
        for a in soup.find_all("a", href=True):
            m = DATE_IN_HREF.search(a["href"])
            if not m:
                continue
            date = dt.date(int(m[1]), int(m[2]), int(m[3]))
            if date < today or a["href"] in seen:
                continue
            seen.add(a["href"])

            # performer sits in a <strong> in the same table cell
            td = a.find_parent("td")
            strong = td.find("strong") if td else None
            summary = strong.get_text(strip=True) if strong else a.get_text(strip=True)

            url = BASE_URL + a["href"].lstrip("/")
            items.append({"url": url, "date": date, "summary": summary})
        return items

    def get_livestream_details(self, item: dict) -> dict:
        soup = self.get_soup(item["url"])
        m = TIME_RE.search(soup.get_text(" ", strip=True))
        if not m:
            raise ValueError(f"no start time on {item['url']}")

        hour, minute, ampm = int(m[1]), int(m[2] or 0), m[3].lower()
        if ampm == "pm" and hour != 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0

        start = dt.datetime.combine(item["date"], dt.time(hour, minute))
        return {
            "start": start,
            "summary": f"{item['summary']} @St. Mary's Perivale",
            "description": YOUTUBE_URL,
        }
