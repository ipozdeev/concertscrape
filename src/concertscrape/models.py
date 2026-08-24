"""Normalized event model shared by every scraper and every publish sink.

This is the single data shape that fixes the old interface mismatch: scrapers
returned two incompatible dict shapes (``start`` as an ISO string vs. as a
``{dateTime, timeZone}`` dict). Now every scraper returns ``list[Event]`` and
every sink (``ics_sink``, ``gcal_sink``) consumes ``Event``.
"""

from __future__ import annotations

import datetime as dt
import hashlib
from dataclasses import dataclass, field

# Livestreams rarely advertise an end time; assume 90 minutes.
DEFAULT_DURATION = dt.timedelta(hours=1, minutes=30)


@dataclass(frozen=True)
class Event:
    """A single upcoming livestream.

    Parameters
    ----------
    start : datetime.datetime
        Timezone-aware start. A naive datetime is rejected so that every event
        carries an unambiguous absolute instant (required for correct
        per-viewer timezone rendering across the US-to-China audience).
    summary : str
        Event title.
    description : str
        Free text; typically the livestream/venue URL.
    url : str | None
        Canonical link to the stream (used for the iCal ``URL`` property and
        de-duplication). Defaults to ``description`` when omitted.
    end : datetime.datetime | None
        Timezone-aware end; defaults to ``start + DEFAULT_DURATION``.
    uid : str
        Stable identifier so regenerated feeds keep event identity for
        subscribers. Derived from ``url`` (or summary+start) when not given.
    """

    start: dt.datetime
    summary: str
    description: str = ""
    url: str | None = None
    end: dt.datetime | None = None
    uid: str = field(default="")

    def __post_init__(self) -> None:
        if self.start.tzinfo is None:
            raise ValueError(f"Event.start must be timezone-aware: {self.start!r}")
        # dataclass is frozen -> use object.__setattr__ to fill derived fields.
        if self.end is None:
            object.__setattr__(self, "end", self.start + DEFAULT_DURATION)
        elif self.end.tzinfo is None:
            raise ValueError(f"Event.end must be timezone-aware: {self.end!r}")
        if not self.url:
            object.__setattr__(self, "url", self.description or None)
        if not self.uid:
            object.__setattr__(self, "uid", self._make_uid())

    def _make_uid(self) -> str:
        """Deterministic UID: prefer the URL, else hash summary + start."""
        seed = self.url or f"{self.summary}|{self.start.isoformat()}"
        digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]
        return f"{digest}@concertscrape"

    def to_gcal_body(self) -> dict:
        """Body for Google Calendar ``events().insert``."""
        return {
            "start": {"dateTime": self.start.isoformat()},
            "end": {"dateTime": self.end.isoformat()},
            "summary": self.summary,
            "description": self.description,
        }
