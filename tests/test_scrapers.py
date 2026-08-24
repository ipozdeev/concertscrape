"""Offline scraper tests: parsing is exercised against saved HTML fixtures,
with ``get_soup`` monkeypatched so no network is touched.
"""

import datetime as dt

import pytz

from concertscrape.scrapers.pcms import SCHEDULE_URL as PCMS_URL
from concertscrape.scrapers.pcms import PCMSScraper
from concertscrape.scrapers.stmary import SCHEDULE_URL as STMARY_URL
from concertscrape.scrapers.stmary import StMaryScraper


def test_stmary_get_events(monkeypatch, fixture_soup):
    schedule = fixture_soup("stmary_schedule.html")
    event = fixture_soup("stmary_event.html")

    def fake_get_soup(url):
        return schedule if url == STMARY_URL else event

    monkeypatch.setattr(StMaryScraper, "get_soup", staticmethod(fake_get_soup))

    events = StMaryScraper().get_events()

    # two future events in the fixture; the past one and "SUMMER BREAK" excluded
    assert len(events) == 2
    first = events[0]
    assert first.summary == "Julian Trevelyan (piano) @St. Mary's Perivale"
    assert first.start.tzinfo is not None
    assert "Europe/London" in str(first.start.tzinfo)
    assert first.start.hour == 14  # "2 pm" from the detail page
    assert first.description.endswith("stmarysperivale2842")


def test_pcms_get_events(monkeypatch, fixture_soup):
    schedule = fixture_soup("pcms_schedule.html")
    event = fixture_soup("pcms_event.html")

    def fake_get_soup(url):
        return schedule if url == PCMS_URL else event

    monkeypatch.setattr(PCMSScraper, "get_soup", staticmethod(fake_get_soup))

    events = PCMSScraper().get_events()

    assert len(events) == 2
    ev = events[0]
    assert ev.summary == "Danika the Rose by PCMS"
    # 3:00 PM New York on May 23, 2021
    expected = pytz.timezone("America/New_York").localize(
        dt.datetime(2021, 5, 23, 15, 0)
    )
    assert ev.start == expected
