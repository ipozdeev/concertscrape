"""Optional Google Calendar mirror.

This is an *optional* sink kept for users who still want events pushed into a
Google Calendar (e.g. running locally on a RaspberryPi with stored OAuth
tokens). It is not needed for the public .ics feed. Requires the ``gcal`` extra
(``uv sync --extra gcal``) and OAuth client secrets.
"""

from __future__ import annotations

import datetime as dt
import logging
import os

import googleapiclient.discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ..models import Event

logger = logging.getLogger("concertscrape.gcal")

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TOKEN_FILE = "token-calendar.json"


def get_calendar_client(creds_file: str):
    """Build a Google Calendar client, running the OAuth flow if needed."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as fh:
            fh.write(creds.to_json())
    return googleapiclient.discovery.build("calendar", "v3", credentials=creds)


def insert_event(event: Event, client, calendar_id: str) -> None:
    """Insert ``event`` unless an event with the same summary already exists."""
    time_min = event.start
    time_max = time_min + dt.timedelta(hours=2)

    existing = (
        client.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )
    for e_ in existing:
        if e_.get("summary") == event.summary:
            logger.info("skip existing: %s", event.summary)
            return

    logger.info("inserting: %s", event.summary)
    client.events().insert(calendarId=calendar_id, body=event.to_gcal_body()).execute()


def push_events(events: list[Event], creds_file: str, calendar_id: str) -> None:
    client = get_calendar_client(creds_file)
    for e_ in events:
        insert_event(e_, client, calendar_id)
