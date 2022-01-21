import abc
import os.path
from bs4 import BeautifulSoup
import requests
import datetime
import pytz
import dateutil.parser
import json

from .youtubetools import get_upcoming_livestreams, get_livestreaming_details

hourandhalf = datetime.timedelta(hours=1, minutes=30)


class ConcertScraper:

    @abc.abstractmethod
    def get_events(self) -> list:
        """Wrapper; get livestream schedule and parse all events.

        Returns
        -------
        list
            of events, each ready to be an event in calendar api; dates are
            in ISO format, time zone-aware
        """
        pass


class YoutubeScraper(ConcertScraper):

    def __init__(self, channel_id, client):
        self.channel_id = channel_id
        self.client = client

    @classmethod
    def by_name(cls, name: str, client):

        with open(os.path.join(os.environ.get("PROJECT_ROOT"),
                               "data/channels.json"), mode="r") as fp:
            channels = json.load(fp)

        if name not in channels:
            raise ValueError("unknown name. channel either erroneously "
                             "spelled or not implemented.")

        return cls(channels[name.lower()], client=client)

    def get_upcoming_livestreams(self, *args, **kwargs) -> list:
        """Get upcoming livestreams."""
        res = get_upcoming_livestreams(self.channel_id, client=self.client,
                                       *args, **kwargs)
        return res

    def video_to_event(self, video_id: (str, list, tuple)):
        """Get livestream details and create event accordingly.

        Parameters
        ----------
        video_id : str or list-like

        Returns
        -------
        list
            of events as dictionaries

        """
        if not isinstance(video_id, str):
            return self.video_to_event(",".join(video_id))

        # create event out of each
        # get details
        ls_details = get_livestreaming_details(video_id, client=self.client)

        # create calendar api-conformable event from details
        events = list()

        for ls_ in ls_details:
            end_time = (dateutil.parser.parse(ls_["start"]) + hourandhalf) \
                .isoformat()
            description = "https://www.youtube.com/watch?v={}" \
                .format(ls_["videoId"])

            event = {
                "start": {
                    "dateTime": ls_["start"],
                },
                "end": {
                    "dateTime": end_time,
                },
                'summary': ls_["title"],
                'description': description,
            }

            events.append(event)

        return events

    def get_events(self, *args, **kwargs) -> list:
        # get livestreams first
        livestreams = self.get_upcoming_livestreams(*args, **kwargs)

        if len(livestreams) < 1:
            # no streams found
            return []

        # convert all video ids to events
        res = self.video_to_event(livestreams)

        return res


class PageScraper(ConcertScraper):
    """Web page scraper.

    Parameters
    ----------
    tz : pytz.timezone
        time zone of the venue
    """

    def __init__(self, tz: pytz.timezone):
        self.tz = tz

    @abc.abstractmethod
    def get_upcoming_livestreams(self) -> list:
        """Collect links to all events present in respective webpage.

        With each link it must be possible to run `get_livestreaming_details()`
        """
        pass

    @abc.abstractmethod
    def get_livestream_details(self, url: str) -> dict:
        """Get details of livestream

        Returns
        -------
        dict
            'start': datetime.datetime (timezone-agnostic),
            'summary': str,
            'description': str
        """
        pass

    @staticmethod
    def get_soup(url: str) -> BeautifulSoup:
        """Convenience method to soupify a page's html."""
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        return soup

    def get_events(self) -> list:
        urls = self.get_upcoming_livestreams()

        events = list()

        for u_ in urls:

            try:
                e_ = self.get_livestream_details(u_)

                # localize start time, add 1.5 hours to event start time
                start_time = self.tz.localize(e_["start"]).isoformat()
                end_time = (self.tz.localize(e_["start"]) + hourandhalf)\
                    .isoformat()

                # create event
                event = {
                    "start": {
                        "dateTime": start_time,
                    },
                    "end": {
                        "dateTime": end_time,
                    },
                    'summary': e_["summary"],
                    'description': e_["description"],
                }

                events.append(event)

            except Exception:
                print(f"failed to get {u_}")

        return events
