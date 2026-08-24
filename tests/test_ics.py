import datetime as dt

import pytz
from icalendar import Calendar

from concertscrape.models import Event
from concertscrape.publish.ics_sink import build_calendar, write_ics


def _event(summary="Concert"):
    tz = pytz.timezone("Europe/Zurich")
    return Event(
        start=tz.localize(dt.datetime(2026, 9, 1, 19, 0)),
        summary=summary,
        description="https://youtube.com/watch?v=abc",
        url="https://youtube.com/watch?v=abc",
    )


def test_build_calendar_roundtrip():
    ics = build_calendar([_event()]).to_ical()
    cal = Calendar.from_ical(ics)
    events = list(cal.walk("VEVENT"))
    assert len(events) == 1
    ev = events[0]
    # stored in UTC; 19:00 Zurich == 17:00 UTC
    assert ev["DTSTART"].dt == dt.datetime(2026, 9, 1, 17, 0, tzinfo=dt.timezone.utc)
    assert str(ev["SUMMARY"]) == "Concert"
    assert str(ev["URL"]) == "https://youtube.com/watch?v=abc"


def test_duration_is_valid_ical():
    ics = build_calendar([_event()]).to_ical().decode()
    assert "REFRESH-INTERVAL;VALUE=DURATION:P1D" in ics
    assert "X-PUBLISHED-TTL:P1D" in ics


def test_write_ics(tmp_path):
    path = write_ics([_event("A"), _event("B")], tmp_path)
    assert path.name == "calendar.ics"
    cal = Calendar.from_ical(path.read_bytes())
    assert len(list(cal.walk("VEVENT"))) == 2
