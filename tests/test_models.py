import datetime as dt

import pytest
import pytz

from concertscrape.models import DEFAULT_DURATION, Event


def _dt(hour=19):
    return pytz.timezone("Europe/Zurich").localize(dt.datetime(2026, 9, 1, hour, 0))


def test_requires_tz_aware_start():
    with pytest.raises(ValueError):
        Event(start=dt.datetime(2026, 9, 1, 19, 0), summary="x")


def test_default_end_and_url():
    e = Event(start=_dt(), summary="Concert", description="https://example/x")
    assert e.end == e.start + DEFAULT_DURATION
    assert e.url == "https://example/x"  # falls back to description


def test_uid_is_stable_and_url_derived():
    a = Event(start=_dt(), summary="Concert", url="https://example/x")
    b = Event(start=_dt(hour=20), summary="Different title", url="https://example/x")
    # same URL -> same UID (dedup key), regardless of summary
    assert a.uid == b.uid
    assert a.uid.endswith("@concertscrape")


def test_gcal_body_shape():
    e = Event(start=_dt(), summary="Concert", description="d")
    body = e.to_gcal_body()
    assert set(body) == {"start", "end", "summary", "description"}
    assert body["start"]["dateTime"].startswith("2026-09-01T19:00:00")
