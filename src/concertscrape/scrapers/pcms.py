"""Philadelphia Chamber Music Society -- livestream schedule from the website."""

from __future__ import annotations

import dateutil.parser
import pytz

from ..registry import register
from .base import PageScraper

SCHEDULE_URL = "https://www.pcmsconcerts.org/concerts/livestreams/"


@register("pcms")
class PCMSScraper(PageScraper):
    def __init__(self):
        super().__init__(pytz.timezone("America/New_York"))

    def get_upcoming_livestreams(self) -> list:
        soup = self.get_soup(SCHEDULE_URL)
        # events sit in a responsive 3-column grid
        cards = soup.find_all("div", class_="col-lg-4 col-md-6")
        return [card.find("a", href=True)["href"] for card in cards]

    def get_livestream_details(self, url: str) -> dict:
        soup = self.get_soup(url)

        info = soup.title.text
        if "Philadelphia" not in info:
            info += " by PCMS"

        # startDate text varies: "Sunday, May 23, 2021 - 3:00 PM" or "... - 2 pm"
        evt_dt = soup.find("span", itemprop="startDate")
        start = dateutil.parser.parse(
            evt_dt.text.replace(" - ", " "), ignoretz=True
        )

        return {"start": start, "summary": info, "description": url}
