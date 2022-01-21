from __future__ import print_function
import datetime
import pickle
import os
import dateutil.parser
import logging

# google
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# id of the calendar with livestreams
calId = os.environ.get("CALENDAR_ID")

logger = logging.getLogger("main.calendar")


def get_calendar_client():
    """Establish connection and set up an API client using credentials.

    Relies on the path to an existing .json file set as an environment
    variable 'GOOGLE_CRED_FILE'.
    """
    logger.info("obtaining calendar handler")
    scopes = ['https://www.googleapis.com/auth/calendar.events']
    creds_file = os.environ.get("GOOGLE_CREDS_FILE")
    api_service_name = "calendar"
    api_version = "v3"

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token-calendar.json'):
        creds = Credentials.from_authorized_user_file('token-calendar.json',
                                                      scopes)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_file, scopes)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token-calendar.json', 'w') as token:
            token.write(creds.to_json())

    service = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=creds
    )

    logger.info("...success!")
    return service


def insert_event(event, client) -> None:
    """Insert event into calendar

    Parameters
    ----------
    event : dict
        "start": {
            "dateTime": datetime.datetime
        },
        "end": [
            "dateTime": datetime.datetimes
        ],
        "summary": str

    client :

    """
    # skip empty events
    if len(event) < 1:
        return

    logger.info(f"inserting event {event.get('summary')}")

    # check if an event exists
    # get all existing events from now
    time_min = dateutil.parser.parse(event["start"]["dateTime"])
    time_max = time_min + datetime.timedelta(hours=2)

    events_result = client.events() \
        .list(calendarId=calId,
              timeMin=time_min.isoformat(),
              timeMax=time_max.isoformat(),
              singleEvents=True, orderBy='startTime')\
        .execute()

    events = events_result.get('items', [])

    for e_ in events:
        eq_summary = e_["summary"] == event["summary"]
        if eq_summary:
            logger.info("such an event exists!")
            return

    event["start"]["dateTime"] = event["start"]["dateTime"]
    event["end"]["dateTime"] = event["end"]["dateTime"]
    client.events().insert(calendarId=calId, body=event).execute()
