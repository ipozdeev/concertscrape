import abc
from bs4 import BeautifulSoup
import requests
import datetime
import pytz
import dateutil.parser

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
    NAME_MAP = {
        "wigmore hall": "UCJEwPH-wbOTa341mZyJ9NSw",
        "royal academy of music": "UCasi3JnYYVlEfJqIgqj92hg",
        "hr-sinfonieorchester": "UCiyuYC0D4-AO0AonCfMifPQ",
        "filharmonia magyarorszag": "UCsFeibl6aoF-qB5OiSZ_XkQ",
        "guerzenich-orchester": "UC9ZTxQYqbsGfBOGvNsaIz8w",
        "het concertgebouw": "UChj95HZDSzcd8MuWDglUmdA",
        "concertgebouworkest": "UCG_xCloLaV2TvXtKOCH-lSA",
        "st.gallen": "UCE2v5mBD7YVToOImrq8o6xg",
        "liszt academy": "UC7WSqFWbljMnGZkXjSgBcag",
        "london so": "UCY1yTIi-DaxPbNtLCnwAM1g",
        "lugano": "UC0neTZR86ezIDoxHaQ5qJHw",
        "malmo so": "UCdJkjJJCaOprC3yQcoflgWg",
        "mariinsky": "UC_FF5Ob7uOYKjtq7kyurt2w",
        "melbourne so": "UCWC3rUkPeaV2B2r_bwwgnNw",
        "mosconstv": "UCDmgUB1w5SJVdIgVqy-Kgwg",
        "mipac": "UCj7IJ427cnavyq2ZOpSKYfA",
        "moscow philharmonic": "UCgXlZFQOYEmrFG-lLlo3HCA",
        "musicchapel": "UCyFMG6Ho-3VgntZDl9lbM1g",
        "nederlands kamerorkest": "UC1u7l5hALHqCZugPh5K86FA",
        "ile-de-france": "UChPZQDc_TzzIPSR9k0Kt75A",
        "orchestre national du capitole": "UCaMYnkGAAxB7_ooo5Wkqn2Q",
        "pcms": "UClmG4E8Ku6jh0R7RKBGZTmw",
        "philharmonia orchestra london": "UCKzx92ZqX1PKYTC-FC-CZRQ",
        "essen": "UCC4Hc8zLmjuiE8siGb4lsbQ",
        "hamburg": "UCeA8g1j18IgOcblnKKvoSZQ",
        "bochum": "UCTQuivksux4qM2Hyo2j4Iuw",
        "scottish co": "UCeZdMMDZ7QlVPHK6lMQV-1g",
        "alla scala": "UCZXldHqCGM5nmD4id4iX7WA",
        "la fenice": "UCkxgPmBI_lVDCy8oiMVheEw",
        "duesseldorf": "UCPBjI43xcci2IoULSVAt1Qw",
        "zurich": "UC9zSsXqNJDkZEfdLJqKBOfA",
        "zaryadye": "UCXTwS82kwA_ByE9wsuvilQg",
        "novosibirsk": "UCZl_OOGXPQSwi7xr0RcO2_g",
        "tomsk": "UCt6GEz9zs9ewpELO14uXF6g",
        "spb": "UCOXb8BpqaKJ-nRQZxQC5oEQ",
        "st.mary": "UC43OVDn283J__YlsucboMlw",
        "massimo": "UC1NTP37ayI-sqRFS76jVDaw",
        "roma tre": "UCFEEHENyE9XkmszXoNMAtlQ",
        "siciliana": "UCB5XcPO7UEvCTsON7nNGxvg",
    }

    def __init__(self, channel_id):
        self.channel_id = channel_id

    @classmethod
    def by_name(cls, name: str):
        if name not in cls.NAME_MAP:
            raise ValueError("unknown name. channel either erroneously "
                             "spelled or not implemented.")

        return cls(cls.NAME_MAP[name.lower()])

    def get_upcoming_livestreams(self, *args, **kwargs) -> list:
        """Get upcoming livestreams."""
        res = get_upcoming_livestreams(self.channel_id, *args, **kwargs)
        return res

    @staticmethod
    def video_to_event(video_id: (str, list, tuple)):
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
            return YoutubeScraper.video_to_event(",".join(video_id))

        # create event out of each
        # get details
        ls_details = get_livestreaming_details(video_id)

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
            except Exception:
                print(f"failed to get {u_}")
                return []

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

        return events
