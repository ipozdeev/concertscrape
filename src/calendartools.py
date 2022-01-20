from __future__ import print_function
import datetime
import pickle
import os
import dateutil.parser

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
PATH_TO_CRED = os.environ.get("GOOGLE_CRED_FILE")

# id of the calendar with livestreams
calId = os.environ.get("CALENDAR_ID")


def get_api_client():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../../token.pickle'):
        with open('../../token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                PATH_TO_CRED, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('../../token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def insert_event(event) -> None:
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

    """
    # skip empty events
    if len(event) < 1:
        return

    # get calendar
    client = get_api_client()

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
            print("nope, such an event exists")
            return

    event["start"]["dateTime"] = event["start"]["dateTime"]
    event["end"]["dateTime"] = event["end"]["dateTime"]
    client.events().insert(calendarId=calId, body=event).execute()

    print("inserted {}\n".format(event["summary"]))
