"""Low-level YouTube Data API v3 helpers.

Every call here reads *public* data (channels / playlistItems / videos / search
``.list``), so a plain **API key** suffices -- no OAuth, which is what lets the
scraper run headless in CI. Set ``YOUTUBE_API_KEY`` in the environment.
"""

from __future__ import annotations

import datetime as dt
import logging

import dateutil.parser
import googleapiclient.discovery
from googleapiclient.errors import HttpError

logger = logging.getLogger("concertscrape.youtube")


def get_youtube_client(api_key: str):
    """Build a read-only YouTube Data API client from an API key."""
    if not api_key:
        raise RuntimeError(
            "YOUTUBE_API_KEY is not set. Create an API key in Google Cloud "
            "console (YouTube Data API v3) and export it as YOUTUBE_API_KEY."
        )
    return googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)


def _get_upcoming_livestreams_low_quota(channel_id: str, client) -> list[str]:
    """videoIds of upcoming livestreams via the channel's uploads playlist.

    Cheap in quota: reads recent uploads and keeps those whose livestream is
    scheduled in the future.
    """
    response_channels = (
        client.channels().list(part="contentDetails", id=channel_id).execute()
    )
    uploads_pl = [
        ch["contentDetails"]["relatedPlaylists"].get("uploads")
        for ch in response_channels.get("items", [])
    ]

    res: list[str] = []
    now = dt.datetime.now(dt.timezone.utc).timestamp()

    for pl_ in uploads_pl:
        if not pl_:
            continue
        try:
            response_videos = (
                client.playlistItems()
                .list(part="contentDetails", playlistId=pl_, maxResults=50)
                .execute()
            )
        except HttpError as err:
            # Some channels expose no accessible uploads playlist (e.g. it is
            # empty or livestream-only) and return 404; skip them gracefully.
            logger.info("uploads playlist %s unavailable: %s", pl_, err.status_code)
            continue
        video_ids = [
            v_["contentDetails"]["videoId"] for v_ in response_videos.get("items", [])
        ]
        if not video_ids:
            continue

        response_ls = (
            client.videos()
            .list(part="liveStreamingDetails", id=",".join(video_ids))
            .execute()
        )
        for ls_ in response_ls.get("items", []):
            details = ls_.get("liveStreamingDetails")
            if not details:
                continue
            start = details.get("scheduledStartTime") or details.get("actualStartTime")
            if not start:
                continue
            if dateutil.parser.parse(start).timestamp() < now:
                continue
            res.append(ls_["id"])

    return res


def _get_upcoming_livestreams_high_quota(channel_id: str, client) -> list[str]:
    """videoIds of upcoming livestreams via search (100 quota units/channel)."""
    response = (
        client.search()
        .list(part="id", channelId=channel_id, type="video", eventType="upcoming")
        .execute()
    )
    return [item["id"]["videoId"] for item in response.get("items", [])]


def get_upcoming_livestreams(
    channel_id: str, client, low_quota: bool = True
) -> list[str]:
    """videoIds of a channel's upcoming livestreams."""
    fn = (
        _get_upcoming_livestreams_low_quota
        if low_quota
        else _get_upcoming_livestreams_high_quota
    )
    return fn(channel_id, client)


def get_livestreaming_details(video_id: str, client) -> list[dict]:
    """Details for one or more (comma-separated) livestream videoIds."""
    response = (
        client.videos()
        .list(part="liveStreamingDetails,snippet", id=video_id)
        .execute()
    )
    out: list[dict] = []
    for e_ in response.get("items", []):
        ls = e_.get("liveStreamingDetails", {})
        start = ls.get("scheduledStartTime") or ls.get("actualStartTime")
        if not start:
            continue
        out.append(
            {
                "channelTitle": e_["snippet"]["channelTitle"],
                "title": e_["snippet"]["title"],
                "description": e_["snippet"]["description"],
                "start": start,
                "videoId": e_["id"],
            }
        )
    return out
