from __future__ import print_function

import logging
import os.path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger("main.email")


def get_gmail_client():
    """Establish connection and set up an API client using credentials."""
    logger.info("obtaining gmail handler")
    scopes = ['https://www.googleapis.com/auth/gmail.send']
    creds_file = os.environ.get("GOOGLE_CREDS_FILE")

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token-gmail.json'):
        creds = Credentials.from_authorized_user_file('token-gmail.json',
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
        with open('token-gmail.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)

        # results = service.users().labels().list(userId='me').execute()
        # labels = results.get('labels', [])
        #
        # if not labels:
        #     print('No labels found.')
        #     return
        # print('Labels:')
        # for label in labels:
        #     print(label['name'])

        logger.info("...success!")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    return service
