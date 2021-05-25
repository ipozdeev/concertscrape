import datetime
import os
import pickle

import dateutil.parser
from joblib import Memory

# google
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.discovery
import googleapiclient.errors

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
PATH_TO_CREDS = '../credentials.json'

cachedir = "./"
memory = Memory(cachedir, verbose=0)


def get_api_client():
    """Establish connection and set up an API client using credentials."""
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # client_secrets_file = "../credentials.json"
    #
    # # Get credentials and create an API client
    creds = None
    # The file token-youtube.pickle stores the user's access and refresh
    # tokens, and is created automatically when the authorization flow
    # completes for the first time.
    if os.path.exists('token-youtube.pickle'):
        with open('token-youtube.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                PATH_TO_CREDS, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token-youtube.pickle', 'wb') as token:
            pickle.dump(creds, token)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=creds)

    return youtube


def _get_upcoming_livestreams_low_quota(channel_id: str):
    # get api client
    youtube = get_api_client()

    request_channels = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )

    response_channels = request_channels.execute()

    # all 'uploads' playlists
    uploads_pl = [
        ch["contentDetails"]["relatedPlaylists"].get("uploads", None)
        for ch in response_channels["items"]
    ]

    # for each playlist, request the videos
    res = list()

    for pl_ in uploads_pl:
        request_videos = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=pl_,
            maxResults=50
        )

        response_videos = request_videos.execute()
        videos = response_videos["items"]

        # filter out livestreams
        video_ids = [v_["contentDetails"]["videoId"] for v_ in videos]

        request_livestreams = youtube.videos().list(
            part="liveStreamingDetails",
            id=",".join(video_ids)
        )
        response_livestreams = request_livestreams.execute()
        livestreams = response_livestreams["items"]

        for ls_ in livestreams:
            ls_details = ls_.get("liveStreamingDetails", False)
            if not ls_details:
                continue
            s_t = ls_details.get("scheduledStartTime",
                                 ls_details["actualStartTime"])
            if dateutil.parser.parse(s_t).timestamp() < \
                    datetime.datetime.today().timestamp():
                continue
            res.append(ls_["id"])

    return res


@memory.cache
def _get_upcoming_livestreams_high_quota(channel_id: str) -> list:
    """Get all upcoming livestreams.

    Parameters
    ----------
    channel_id : str
        e.g. 'UCasi3JnYYVlEfJqIgqj92hg'

    Returns
    -------
    res : list
        of video ids
    """
    # get api client
    youtube = get_api_client()

    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        type="video",
        eventType="upcoming"
    )

    response = request.execute()

    res = [ls_["id"]["videoId"] for ls_ in response["items"]]

    return res


def get_upcoming_livestreams(channel_id: str, low_quota: bool = True) -> list:
    """Get list of video ids of upcoming livestreams on a channel.

    Parameters
    ----------
    channel_id : str
        one channel id (no possibility of multiple channels as of 2021)
    low_quota : bool
        False to use the expensive search (100 quota points per `channel_id`)

    """
    if low_quota:
        f = _get_upcoming_livestreams_low_quota
    else:
        f = _get_upcoming_livestreams_high_quota

    return f(channel_id)


@memory.cache
def get_livestreaming_details(video_id: str) -> list:
    """Get livestreaming details of a video.

    Parameters
    ----------
    video_id : str
        comma-separated video ids, each video must be a livestream
    """
    # get api client
    youtube = get_api_client()

    # get video element
    request = youtube.videos().list(
        part="liveStreamingDetails,snippet",
        id=video_id
    )
    response_list = request.execute()["items"]

    res = [
        {"channelTitle": e_["snippet"]["channelTitle"],
         "title": e_["snippet"]["title"],
         "description": e_["snippet"]["description"],
         "start": e_["liveStreamingDetails"]["scheduledStartTime"],
         "videoId": e_["id"]}
        for e_ in response_list
    ]

    return res


if __name__ == "__main__":
    pass
