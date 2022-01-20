import json

from setup import *

from src.calendartools import insert_event
from src.core import YoutubeScraper
from src.scrapers import StMaryScraper


def insert_video_event(video_id):
    e_ = YoutubeScraper.video_to_event(video_id)[0]
    insert_event(e_)


def scrape_stmary() -> None:
    """Scrape St. Mary's Perivale events (from website)."""
    events = StMaryScraper().get_events()

    for e_ in events:
        insert_event(e_)


def scrape_youtube() -> None:
    """Scrape all youtube channels."""
    with open("data/channels.json", mode="r") as fp:
        channels = json.load(fp)

    for ch_name in list(channels.keys()):
        try:
            scr = YoutubeScraper.by_name(ch_name)
            events = scr.get_events(low_quota=False)
            for e_ in events:
                insert_event(e_)
        except Exception:
            print(f"something off with {ch_name}")


if __name__ == '__main__':
    scrape_youtube()
