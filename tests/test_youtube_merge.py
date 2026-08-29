"""Offline tests for merging the two upcoming-livestream discovery methods.

A tiny fake stands in for the YouTube client so no network/quota is used.
"""

import types

from googleapiclient.errors import HttpError

from concertscrape.youtube import get_merged_upcoming_livestreams

FUTURE = "2099-01-01T00:00:00Z"


class _Req:
    def __init__(self, result=None, exc=None):
        self._result, self._exc = result, exc

    def execute(self):
        if self._exc:
            raise self._exc
        return self._result


class _Resource:
    def __init__(self, handler):
        self._handler = handler

    def list(self, **kwargs):
        return self._handler(kwargs)


class FakeClient:
    """Returns ``uploads_ids`` from the uploads scan and ``search_ids`` from search."""

    def __init__(self, uploads_ids, search_ids, search_exc=None):
        self._uploads_ids = uploads_ids
        self._search_ids = search_ids
        self._search_exc = search_exc

    def channels(self):
        uploads = {"relatedPlaylists": {"uploads": "UU1"}}
        result = {"items": [{"contentDetails": uploads}]}
        return _Resource(lambda kw: _Req(result))

    def playlistItems(self):
        items = [{"contentDetails": {"videoId": v}} for v in self._uploads_ids]
        return _Resource(lambda kw: _Req({"items": items}))

    def videos(self):
        def handler(kw):
            ids = kw["id"].split(",") if kw.get("id") else []
            ls = {"scheduledStartTime": FUTURE}
            items = [{"id": v, "liveStreamingDetails": ls} for v in ids]
            return _Req({"items": items})

        return _Resource(handler)

    def search(self):
        if self._search_exc:
            return _Resource(lambda kw: _Req(exc=self._search_exc))
        items = [{"id": {"videoId": v}} for v in self._search_ids]
        return _Resource(lambda kw: _Req({"items": items}))


def test_merge_unions_and_preserves_order_dropping_dupes():
    client = FakeClient(uploads_ids=["A", "B"], search_ids=["B", "C"])
    assert get_merged_upcoming_livestreams("UCx", client) == ["A", "B", "C"]


def test_merge_survives_search_failure():
    exc = HttpError(types.SimpleNamespace(status=403, reason="quotaExceeded"), b"{}")
    client = FakeClient(uploads_ids=["A", "B"], search_ids=[], search_exc=exc)
    # search 403s, but the uploads results still come through
    assert get_merged_upcoming_livestreams("UCx", client) == ["A", "B"]
