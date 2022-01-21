import datetime
import os
import pickle
import logging
import dateutil.parser
from joblib import Memory

# google
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.discovery

cachedir = os.environ.get("PROJECT_ROOT")
memory = Memory(cachedir, verbose=0)

logger = logging.getLogger("main.youtube")


def get_youtube_client():
    """Establish connection and set up an API client using credentials.

    Relies on the path to an existing .json file set as an environment
    variable 'GOOGLE_CRED_FILE'.
    """
    logger.info("obtaining youtube handler")

    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    creds_file = os.environ.get("GOOGLE_CREDS_FILE")

    # # Disable OAuthlib's HTTPS verification when running locally.
    # # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token-youtube.json'):
        creds = Credentials.from_authorized_user_file('token-youtube.json',
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
        with open('token-youtube.json', 'w') as token:
            token.write(creds.to_json())

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=creds
    )

    logger.info("...success!")

    return youtube


def _get_upcoming_livestreams_low_quota(channel_id: str, client) -> list:
    """Get videoId of upcoming livestreams.

    Retrieves videos with liveStreamingDetails from the uploads playlist of
    a channel; this is a cheap (in terms of quota) query.

    Parameters
    ----------
    channel_id : str
        e.g. 'UCasi3JnYYVlEfJqIgqj92hg'
    client : Resource

    Returns
    -------
    res : list
        of video ids
    """
    request_channels = client.channels().list(
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
        request_videos = client.playlistItems().list(
            part="contentDetails",
            playlistId=pl_,
            maxResults=50
        )

        response_videos = request_videos.execute()
        videos = response_videos["items"]

        # filter out livestreams
        video_ids = [v_["contentDetails"]["videoId"] for v_ in videos]

        request_livestreams = client.videos().list(
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
                                 ls_details.get("actualStartTime", "no time"))
            if dateutil.parser.parse(s_t).timestamp() < \
                    datetime.datetime.today().timestamp():
                continue
            res.append(ls_["id"])

    return res


@memory.cache
def _get_upcoming_livestreams_high_quota(channel_id: str, client) -> list:
    """Get videoId of upcoming livestreams.

    Retrieves all videos from a channel, where evenType='upcoming'; this is an
    expensive (in terms of quota) query.

    Parameters
    ----------
    channel_id : str
        e.g. 'UCasi3JnYYVlEfJqIgqj92hg'
    client : Resource

    Returns
    -------
    res : list
        of video ids
    """
    request = client.search().list(
        part="id",
        channelId=channel_id,
        type="video",
        eventType="upcoming"
    )

    response = request.execute()

    res = [ls_["id"]["videoId"] for ls_ in response["items"]]

    return res


def get_upcoming_livestreams(channel_id: str,
                             client,
                             low_quota: bool = True) -> list:
    """Get videoId of upcoming livestreams (wrapper).

    Parameters
    ----------
    channel_id : str
        one channel id (no possibility of multiple channels as of 2021)
    client : Resource
    low_quota : bool
        False to use the expensive search (100 quota points per `channel_id`)

    """
    if low_quota:
        f = _get_upcoming_livestreams_low_quota
    else:
        f = _get_upcoming_livestreams_high_quota

    return f(channel_id, client)


@memory.cache
def get_livestreaming_details(video_id: str, client) -> list:
    """Get livestreaming details of a video.

    Parameters
    ----------
    video_id : str
        comma-separated video ids, each video must be a livestream
    client : Resource
    """
    # get video element
    request = client.videos().list(
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
