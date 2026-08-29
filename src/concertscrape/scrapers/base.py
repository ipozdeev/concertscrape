"""Scraper base classes. Every scraper produces ``list[Event]``.

Two families:

* ``PageScraper`` -- HTML venue pages. Subclasses implement
  ``get_upcoming_livestreams()`` (collect items/links) and
  ``get_livestream_details(item)`` (parse one item into a *naive* start +
  summary + description). The base localizes to the venue timezone and builds
  the ``Event``.
* ``YoutubeScraper`` -- a YouTube channel; details come from the Data API.
"""

from __future__ import annotations

import abc
import datetime as dt
import json
import logging
from importlib import resources

import dateutil.parser
import requests
from bs4 import BeautifulSoup

from ..models import Event
from ..youtube import get_livestreaming_details, get_merged_upcoming_livestreams

logger = logging.getLogger("concertscrape.scrapers")


class ConcertScraper(abc.ABC):
    @abc.abstractmethod
    def get_events(self) -> list[Event]:
        """Return all upcoming livestream events for this source."""


class PageScraper(ConcertScraper):
    """Scraper for a venue's HTML schedule page.

    Parameters
    ----------
    tz : datetime.tzinfo
        Timezone of the venue; used to localize the naive datetimes that
        ``get_livestream_details`` returns.
    """

    def __init__(self, tz: dt.tzinfo):
        self.tz = tz

    @abc.abstractmethod
    def get_upcoming_livestreams(self) -> list:
        """Collect the items (links or tags) for each upcoming event.

        Each item must be consumable by ``get_livestream_details``.
        """

    @abc.abstractmethod
    def get_livestream_details(self, item) -> dict:
        """Parse one item into ``{"start", "summary", "description"}``.

        ``start`` must be a **naive** ``datetime`` in the venue's local time;
        the base class localizes it with ``self.tz``.
        """

    @staticmethod
    def get_soup(url: str) -> BeautifulSoup:
        """Fetch ``url`` and return parsed HTML."""
        page = requests.get(url, timeout=30, headers={"User-Agent": "concertscrape"})
        page.raise_for_status()
        return BeautifulSoup(page.content, "html.parser")

    def get_events(self) -> list[Event]:
        events: list[Event] = []
        for item in self.get_upcoming_livestreams():
            try:
                detail = self.get_livestream_details(item)
                start = self.tz.localize(detail["start"])
                events.append(
                    Event(
                        start=start,
                        summary=detail["summary"],
                        description=detail.get("description", ""),
                    )
                )
            except Exception as err:  # one bad row must not sink the batch
                logger.warning("failed to parse an item: %s", err)
        return events


def load_channels() -> dict[str, str]:
    """Load the YouTube channel map bundled with the package."""
    data = resources.files("concertscrape").joinpath("data/channels.json")
    return json.loads(data.read_text(encoding="utf-8"))


class YoutubeScraper(ConcertScraper):
    """Scraper for a single YouTube channel's upcoming livestreams."""

    def __init__(self, channel_id: str, client):
        self.channel_id = channel_id
        self.client = client

    @classmethod
    def by_name(cls, name: str, client) -> YoutubeScraper:
        channels = load_channels()
        key = name.lower()
        if key not in channels:
            raise ValueError(f"unknown channel {name!r} (not in channels.json)")
        return cls(channels[key], client=client)

    def get_events(self) -> list[Event]:
        video_ids = get_merged_upcoming_livestreams(
            self.channel_id, client=self.client
        )
        if not video_ids:
            return []

        details = get_livestreaming_details(",".join(video_ids), client=self.client)

        events: list[Event] = []
        for d_ in details:
            start = dateutil.parser.parse(d_["start"])  # tz-aware ISO from API
            url = f"https://www.youtube.com/watch?v={d_['videoId']}"
            events.append(
                Event(
                    start=start,
                    summary=d_["title"],
                    description=url,
                    url=url,
                )
            )
        return events
