"""Build and write the canonical ``calendar.ics`` feed from a list of events.

The feed is a full snapshot of currently-known upcoming livestreams, so it is
regenerated from scratch each run. Stable per-event ``UID``s (see
``Event._make_uid``) keep event identity across regenerations for subscribers.
Times are emitted in UTC; subscribers' apps render them in the local timezone.
"""

from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path

from icalendar import Calendar, vDuration
from icalendar import Event as IcalEvent

from ..models import Event

logger = logging.getLogger("concertscrape.ics")

CALENDAR_NAME = "Classical concert livestreams"
# Ask subscribing clients to refresh roughly daily.
REFRESH_INTERVAL = dt.timedelta(days=1)


def build_calendar(events: list[Event]) -> Calendar:
    cal = Calendar()
    cal.add("prodid", "-//concertscrape//classical livestreams//EN")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", CALENDAR_NAME)
    cal.add("name", CALENDAR_NAME)
    # RFC 7986 REFRESH-INTERVAL + the widely-honored X-PUBLISHED-TTL hint,
    # both as iCalendar DURATION values (e.g. "P1D").
    refresh = vDuration(REFRESH_INTERVAL)
    refresh.params["VALUE"] = "DURATION"
    cal.add("refresh-interval", refresh)
    cal.add("x-published-ttl", vDuration(REFRESH_INTERVAL))

    now = dt.datetime.now(dt.timezone.utc)
    for e_ in events:
        comp = IcalEvent()
        comp.add("uid", e_.uid)
        comp.add("dtstamp", now)
        comp.add("dtstart", e_.start.astimezone(dt.timezone.utc))
        comp.add("dtend", e_.end.astimezone(dt.timezone.utc))
        comp.add("summary", e_.summary)
        if e_.description:
            comp.add("description", e_.description)
        if e_.url:
            comp.add("url", e_.url)
        cal.add_component(comp)

    return cal


def write_ics(events: list[Event], output_dir: str | Path) -> Path:
    """Write ``<output_dir>/calendar.ics`` and return its path."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "calendar.ics"
    path.write_bytes(build_calendar(events).to_ical())
    logger.info("wrote %d events to %s", len(events), path)
    return path
