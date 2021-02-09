import unittest
import datetime
import pytz

from ..scraper import (WigmoreHallScraper, PSCMScraper, ZeneakademiaScraper)


# TODO: finish setUpClass
# class ScraperTestCase(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls, scraper, tz, start_time, summary) -> None:
#         """
#
#         Parameters
#         ----------
#         scraper
#         tz
#         start_time
#         summary
#
#         Returns
#         -------
#
#         """
#         cls.scraper = scraper
#         cls.tz = tz
#         cls.startTime = tz.localize(start_time)
#         cls.summary = summary


@unittest.skip
class TestWigmoreHallScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = WigmoreHallScraper()
        self.tz = pytz.timezone("Europe/London")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 2, 15, 19, 30))
        self.summary = "Anon, Browne, Cornysh and more by The Sixteen"

    def test_get_event(self):
        url = "https://wigmore-hall.org.uk/whats-on/the-sixteen-202102151930"
        res_event = self.scraper.get_event(url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"], dict(dateTime=self.startTime,
                                                  timeZone=self.tz.zone))


class TestPSCMScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = PSCMScraper()
        self.tz = pytz.timezone("America/New_York")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 2, 10, 18))
        self.summary = "Anthony McGill, clarinet; " \
                       "Milena Pajaro-van de Stadt, viola; " \
                       "Gloria Chien, piano - " \
                       "Philadelphia Chamber Music Society"

    def test_get_event(self):
        url = "https://www.pcmsconcerts.org/concerts/" \
              "mcgill-pajaro-van-de-stadt-chien/"
        res_event = self.scraper.get_event(url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"],
                         dict(dateTime=self.startTime.isoformat(),
                              timeZone=self.tz.zone))


class TestZeneakademiaScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = ZeneakademiaScraper()
        self.tz = pytz.timezone("Europe/Budapest")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 2, 9, 19, 30))
        self.summary = "Cziffra's Heritage by Liszt Academy"

    # @unittest.skip
    def test_get_event(self):
        url = "https://zeneakademia.hu/all-programs/" \
              "2021-02-09-cziffras-heritage-9753"
        res_event = self.scraper.get_event(url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"],
                         dict(dateTime=self.startTime.isoformat(),
                              timeZone=self.tz.zone))

    def test_get_event_schedule(self):
        res = self.scraper.get_event_schedule()
        self.assertGreater(len(res), 0)
