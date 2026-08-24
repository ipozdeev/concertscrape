"""Template for a new venue scraper.

Copy this file to ``concertscrape/scrapers/<venue>.py``, fill in the two
methods, then register it by adding an import in
``concertscrape/scrapers/__init__.py``:

    from . import <venue>  # noqa: F401

See ``stmary.py`` and ``pcms.py`` for real, working examples.
"""

from __future__ import annotations

import datetime as dt

import pytz

from concertscrape.registry import register
from concertscrape.scrapers.base import PageScraper

SCHEDULE_URL = "https://example.org/livestreams"


@register("myvenue")  # <- unique name; also used in logs
class MyVenueScraper(PageScraper):
    def __init__(self):
        # Use the venue's IANA timezone so start times localize correctly.
        super().__init__(pytz.timezone("Europe/Zurich"))

    def get_upcoming_livestreams(self) -> list:
        """Return a list of items (usually event-page URLs) to parse.

        Each item is passed, one at a time, to ``get_livestream_details``.
        """
        soup = self.get_soup(SCHEDULE_URL)
        return [a["href"] for a in soup.select("a.event-link[href]")]

    def get_livestream_details(self, item) -> dict:
        """Parse one item into start / summary / description.

        ``start`` MUST be a *naive* datetime in the venue's local time; the base
        class localizes it with ``self.tz`` and builds the ``Event`` (adding a
        default 90-minute end and a stable UID).
        """
        soup = self.get_soup(item)
        start = dt.datetime.strptime(
            soup.select_one(".date").text.strip(), "%d %B %Y %H:%M"
        )
        return {
            "start": start,
            "summary": soup.select_one("h1").text.strip(),
            "description": item,  # link to the stream/event page
        }
