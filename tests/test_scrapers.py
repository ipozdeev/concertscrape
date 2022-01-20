import unittest
import datetime
from unittest import TestCase

import pytz

from concertscrape.src.scrapers import (PCMSScraper, ZeneakademiaScraper,
                                        AllaScalaScraper, MagyarorszagScraper, MalmoScraper,
                                        HrScraper, SCOScraper, StMaryScraper)


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
        self.stream_url = \
            "https://www.pcmsconcerts.org/concerts/danika-the-rose/"
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 5, 23, 15))
        self.summary = "Danika the Rose"

    @unittest.skip
    def test_get_livestreaming_details(self):
        res_event = self.scraper.get_livestream_details(self.stream_url)

        self.assertEqual(res_event["summary"], self.summary)
        self.assertEqual(res_event["start"], self.startTime)

    @unittest.skip
    def test_get_upcoming_livestreams(self):
        res = self.scraper.get_upcoming_livestreams()
        self.assertGreater(len(res), 0)


@unittest.skip
class TestZeneakademiaScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = ZeneakademiaScraper()
        self.tz = pytz.timezone("Europe/Budapest")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 2, 9, 19, 30))
        self.summary = "Cziffra's Heritage by Liszt Academy"

    @unittest.skip
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

    @unittest.skip
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

    @unittest.skip
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


@unittest.skip
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
            self.tz.localize(datetime.datetime(2021, 5, 20, 20, 0))
        self.summary = "Schuberts »Große Sinfonie«"

    def test_get_event_schedule(self):
        res = self.scraper.get_event_schedule()
        self.assertGreater(len(res), 1)

    def test__get_event(self):
        url = "https://www.hr-sinfonieorchester.de/livestreams/" \
              "schuberts-grosse-sinfonie,livestream-20-05-2021-100.html"
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


@unittest.skip
class TestStMaryScraper(TestCase):
    def setUp(self) -> None:
        self.scraper = StMaryScraper()
        self.tz = pytz.timezone("Europe/London")
        self.startTime = \
            self.tz.localize(datetime.datetime(2021, 10, 5, 15, 0))
        self.summary = "Alicja Fiderkiewicz (piano)"

    def test_get_upcoming_livestreams(self):
        res = self.scraper.get_upcoming_livestreams()
        self.assertGreater(len(res), 1)
