import json

from setup import *

from src.calendartools import insert_event, get_calendar_client
from src.youtubetools import get_youtube_client
from src.core import YoutubeScraper
from src.scrapers import StMaryScraper
from src.utils import logger


def scrape_stmary() -> None:
    """Scrape St. Mary's Perivale events (from website)."""
    # load clients
    calendar_client = get_calendar_client()

    events = StMaryScraper().get_events()

    for e_ in events:
        insert_event(e_, calendar_client)


def scrape_youtube() -> None:
    """Scrape all youtube channels."""
    with open("data/channels.json", mode="r") as fp:
        channels = json.load(fp)

    # load clients
    calendar_client = get_calendar_client()
    youtube_client = get_youtube_client()

    # loop over channels
    for ch_name in list(channels.keys()):
        logger.info(f"channel {ch_name}...")
        try:
            # get events
            scr = YoutubeScraper.by_name(ch_name, client=youtube_client)
            events = scr.get_events(low_quota=False)

            # for each event, insert it into the calendar
            for e_ in events:
                insert_event(e_, calendar_client)

        except Exception as err:
            logger.error(str(err))

    logger.info("all done!")


if __name__ == '__main__':
    scrape_youtube()
