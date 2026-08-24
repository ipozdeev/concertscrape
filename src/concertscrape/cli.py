"""Command-line entry point: scrape all sources, then publish.

Usage
-----
    concertscrape run                 # scrape -> write docs/calendar.ics
    concertscrape run --gcal          # also mirror into Google Calendar
    concertscrape run -o public       # write to a different output dir
"""

from __future__ import annotations

import argparse
import logging

from . import scrapers  # noqa: F401  (import registers the live page scrapers)
from .config import load_settings
from .logging_setup import configure_logging
from .models import Event
from .publish.ics_sink import write_ics
from .registry import registered_scrapers
from .scrapers.base import YoutubeScraper, load_channels
from .youtube import get_youtube_client

logger = logging.getLogger("concertscrape.cli")


def collect_events(youtube_api_key: str | None) -> list[Event]:
    """Run every source (YouTube channels + page scrapers) and gather events."""
    events: list[Event] = []

    # --- YouTube channels ---
    if youtube_api_key:
        client = get_youtube_client(youtube_api_key)
        for name in load_channels():
            logger.info("youtube: %s", name)
            try:
                events.extend(YoutubeScraper.by_name(name, client=client).get_events())
            except Exception as err:
                logger.error("youtube %s failed: %s", name, err)
    else:
        logger.warning("YOUTUBE_API_KEY not set -- skipping YouTube channels")

    # --- Page scrapers (registered live venues) ---
    for name, factory in registered_scrapers().items():
        logger.info("page: %s", name)
        try:
            events.extend(factory().get_events())
        except Exception as err:
            logger.error("page %s failed: %s", name, err)

    return events


def dedupe(events: list[Event]) -> list[Event]:
    """Drop events sharing a UID, keeping first occurrence."""
    seen: set[str] = set()
    out: list[Event] = []
    for e_ in events:
        if e_.uid in seen:
            continue
        seen.add(e_.uid)
        out.append(e_)
    return out


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="concertscrape")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="scrape all sources and publish the .ics feed")
    run_p.add_argument(
        "-o", "--output-dir", default=None, help="output directory (default: docs)"
    )
    run_p.add_argument(
        "--gcal",
        action="store_true",
        help="also mirror events into Google Calendar (needs the 'gcal' extra)",
    )

    args = parser.parse_args(argv)
    configure_logging()
    settings = load_settings()

    output_dir = args.output_dir or settings.output_dir

    events = dedupe(collect_events(settings.youtube_api_key))
    events.sort(key=lambda e: e.start)
    logger.info("collected %d unique events", len(events))

    path = write_ics(events, output_dir)
    logger.info("wrote %s", path)

    if args.gcal:
        if not settings.gcal_enabled:
            logger.error("--gcal set but CALENDAR_ID / GOOGLE_CREDS_FILE missing")
            return 1
        from .publish.gcal_sink import push_events

        push_events(events, settings.google_creds_file, settings.calendar_id)

    logger.info("done")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
