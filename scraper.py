import abc
from bs4 import BeautifulSoup
import requests
import datetime
import pytz
import re


class ConcertScraper:

    def __init__(self, tz):
        self.tz = tz
        self.timedelta = datetime.timedelta(hours=1, minutes=30)

    @abc.abstractmethod
    def _get_event(self, url: str) -> dict:
        """

        Parameters
        ----------
        url

        Returns
        -------
        dict
            {'start': {'dateTime': `datetime.datetime()`,
                       'timeZone': `str`},
             'end': <same>}

        """
        pass

    def get_event(self, url: str) -> dict:
        """Create calendar-ready event from info in url.

        This is a wrapper to add end time autimatically as startTime + 1.5 hrs.

        Parameters
        ----------
        url : str

        Returns
        -------
        dict

        """
        evt = self._get_event(url)
        evt["end"] = {
            'dateTime': (evt["start"]["dateTime"] + self.timedelta) \
                .isoformat(),
            'timeZone': evt["start"]["timeZone"],
        }
        evt["start"]["dateTime"] = evt["start"]["dateTime"].isoformat()

        return evt

    @abc.abstractmethod
    def get_event_schedule(self) -> list:
        """Collect links to all events present at a webpage.

        On each link it must be possible to run `self.get_event()`.
        """
        pass


class WigmoreHallScraper(ConcertScraper):

    def _get_event(self, url: str) -> dict:

        # TODO: bs4 doesn't work; use selenium or whatever

        pass

    def get_event_schedule(self) -> list:
        pass


class PCMSScraper(ConcertScraper):
    def __init__(self):
        super(PCMSScraper, self).__init__(pytz.timezone("America/New_York"))

    def _get_event(self, url: str) -> dict:

        # parse, create soup
        # TODO: relocate to parent
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        # info, in the title of the page
        info = soup.title.text
        if "Philadelphia" not in info:
            info += " by PCMS"

        # start date
        evt_dt = soup.find("span", itemprop="startDate")
        evt_dt = datetime.datetime.strptime(evt_dt.text,
                                            "%A, %B %d, %Y - %I:%M %p")
        evt_dt = self.tz.localize(evt_dt)

        # return
        res = {
            "start": {
                "dateTime": evt_dt,
                "timeZone": self.tz.zone
            },
            'summary': info,
            'description': url,
        }

        return res

    def get_event_schedule(self):
        url = "https://www.pcmsconcerts.org/concerts/livestreams/"

        # get content, create soup
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        # events are in the grid of 3 columns
        events = soup.find_all("div", class_="col-lg-4 col-md-6")

        res = list()
        for e_ in events:
            href = e_.find('a', href=True)["href"]
            res.append(href)

        return res


class ZeneakademiaScraper(ConcertScraper):
    def __init__(self):
        super(ZeneakademiaScraper, self)\
            .__init__(pytz.timezone("Europe/Budapest"))

    def get_event_schedule(self):
        url = "https://zeneakademia.hu/streaming"

        # get content, create soup
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        # links are relative (!) hrefs in articles
        events = soup.find_all("article", class_="event soldout")

        res = list()
        for e_ in events:
            href = e_.find_all('a', href=True)[-1]["href"]
            res.append("https://zeneakademia.hu" + href)

        return res

    def _get_event(self, url: str) -> dict:
        # parse, create soup
        # TODO: relocate to parent
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        # start date
        regexpr = "[0-9]+ [A-Za-z]+ [0-9]{4}, [0-9]+[.][0-9]{2}"
        evt_dt_tag = soup.find("h2", text=re.compile(regexpr))
        evt_dt = evt_dt_tag.text.split("-")[0]
        evt_dt = datetime.datetime.strptime(evt_dt, "%d %B %Y, %H.%M")
        evt_dt = self.tz.localize(evt_dt)

        # info, in the sibling of the date's grand-parent
        info_tag = evt_dt_tag.find_parent().find_parent().find_next_sibling()
        info = info_tag.text

        if "Liszt Academy" not in info:
            info += " by Liszt Academy"

        # return
        res = {
            "start": {
                "dateTime": evt_dt,
                "timeZone": self.tz.zone
            },
            'summary': info,
            'description': url,
        }

        return res


if __name__ == '__main__':
    pass
