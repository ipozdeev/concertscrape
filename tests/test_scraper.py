import unittest
import datetime
from unittest import TestCase

import pytz

from ..scraper import (PCMSScraper, ZeneakademiaScraper,
                       AllaScalaScraper, MagyarorszagScraper, MalmoScraper,
                       HrScraper, SCOScraper)


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
class TestPCMSScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = PCMSScraper()
        self.tz = pytz.timezone("America/New_York")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 2, 10, 18))
        self.summary = "Anthony McGill, clarinet; " \
                       "Milena Pajaro-van de Stadt, viola; " \
                       "Gloria Chien, piano - " \
                       "Philadelphia Chamber Music Society"

    # @unittest.skip
    def test_get_event(self):
        url = "https://www.pcmsconcerts.org/concerts/" \
              "mcgill-pajaro-van-de-stadt-chien/"
        res_event = self.scraper.get_event(url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"],
                         dict(dateTime=self.startTime.isoformat(),
                              timeZone=self.tz.zone))

    def test_get_event_schedule(self):
        res = self.scraper.get_event_schedule()
        self.assertGreater(len(res), 0)


@unittest.skip
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


@unittest.skip
class TestAllaScalaScraper(TestCase):
    def setUp(self) -> None:
        self.scraper = AllaScalaScraper()
        self.tz = pytz.timezone("Europe/Rome")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 3, 5, 18, 0))
        self.summary = "Myung-Whun Chung at Teatro alla Scala"

    def test__get_event(self):
        url = "https://www.teatroallascala.org/en/season/2020-2021/concert/" \
              "symphony-concert/myung-whun-chung.html"

        res_event = self.scraper.get_event(url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"],
                         dict(dateTime=self.startTime.isoformat(),
                              timeZone=self.tz.zone))

    def test_get_event_schedule(self):
        res = self.scraper.get_event_schedule()
        self.assertGreater(len(res), 0)


@unittest.skip
class TestMagyarorszagScraper(TestCase):
    def setUp(self) -> None:
        self.scraper = MagyarorszagScraper()
        self.tz = pytz.timezone("Europe/Budapest")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 3, 4, 19, 0))
        self.summary = "Kodály Kórus Debrecen by Filharmónia Magyarország"

    def test__get_event(self):
        url = "http://filharmonia.hu/program/kodaly-korus-debrecen/"
        res_event = self.scraper.get_event(url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"],
                         dict(dateTime=self.startTime.isoformat(),
                              timeZone=self.tz.zone))

    def test_get_event_schedule(self):
        res = self.scraper.get_event_schedule()
        self.assertGreater(len(res), 0)


# @unittest.skip
class TestMalmoScraper(TestCase):
    def setUp(self) -> None:
        self.scraper = MalmoScraper()
        self.tz = pytz.timezone("Europe/Stockholm")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 4, 8, 19, 0))
        self.summary = "MSO Live: Shostakovich on piano"

    def test_get_event_schedule(self):
        res = self.scraper.get_event_schedule()
        self.assertGreater(len(res), 0)

    def test__get_event(self):
        url = "https://malmolive.se/en/program/mso-live-shostakovich-on-piano"
        res_event = self.scraper.get_event(url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"],
                         dict(dateTime=self.startTime.isoformat(),
                              timeZone=self.tz.zone))


@unittest.skip
class TestHrScraper(TestCase):
    def setUp(self) -> None:
        self.scraper = HrScraper()
        self.tz = pytz.timezone("Europe/Berlin")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 3, 11, 20, 0))
        self.summary = "Music Discovery Project 2021"

    def test_get_event_schedule(self):
        res = self.scraper.get_event_schedule()
        self.assertGreater(len(res), 1)

    def test__get_event(self):
        url = "https://www.hr-sinfonieorchester.de/livestreams/" \
              "music-discovery-project-2021,livestream-11-03-2021-100.html"
        res_event = self.scraper.get_event(url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"],
                         dict(dateTime=self.startTime.isoformat(),
                              timeZone=self.tz.zone))


@unittest.skip
class TestSCOScraper(TestCase):
    def setUp(self) -> None:
        self.scraper = SCOScraper()
        self.tz = pytz.timezone("Europe/London")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 4, 15, 19, 30))
        self.summary = "Caplet, Clyne & Dvořák"

    def test_get_event_schedule(self):
        res = self.scraper.get_event_schedule()
        self.assertGreater(len(res), 1)

    def test__get_event(self):
        url = "https://www.sco.org.uk/events/caplet-clyne-dvořák-1"
        res_event = self.scraper.get_event(url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"],
                         dict(dateTime=self.startTime.isoformat(),
                              timeZone=self.tz.zone))
