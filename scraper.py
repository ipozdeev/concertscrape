from bs4 import BeautifulSoup
import requests
import datetime
import pytz


class ConcertScraper:

    def __init__(self, tz):
        self.tz = tz

    def get_event(self, url: str) -> dict:
        """

        Parameters
        ----------
        url : str

        Returns
        -------
        dict

        """
        pass

    # TODO: decorators for event duration


class WigmoreHallScraper(ConcertScraper):

    def get_event(self, url: str) -> dict:

        #TODO: use selenium here

        pass


class PSCMScraper(ConcertScraper):
    def __init__(self):
        super(PSCMScraper, self).__init__(pytz.timezone("America/New_York"))

    def get_event(self, url: str) -> dict:

        # parse, create soup
        # TODO: relocate to parent
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        # info, in the title of the page
        summ = soup.title.text

        # start date
        evt_dt = soup.find("span", itemprop="startDate")
        evt_dt = datetime.datetime.strptime(evt_dt.text,
                                            "%A, %B %d, %Y - %I:%M %p")
        evt_dt = self.tz.localize(evt_dt)

        # return
        res = {
            "start": {
                "dateTime": evt_dt.isoformat(),
                "timeZone": self.tz.zone
            },
            'summary': summ,
            'description': url,
        }

        return res


if __name__ == '__main__':
    pass
