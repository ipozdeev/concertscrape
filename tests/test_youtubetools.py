import unittest
from src.youtubetools import (get_upcoming_livestreams, get_api_client,
                              get_livestreaming_details)


class Test(unittest.TestCase):

    def test_youtube_init(self):
        yt = get_api_client()

    @unittest.skip
    def test_get_upcoming_livestreams(self):
        channel_id = "UCJEwPH-wbOTa341mZyJ9NSw"
        ls = get_upcoming_livestreams(channel_id, low_quota=True)
        print(ls)

    @unittest.skip
    def test_get_livestreaming_details(self):
        video_id = "eKfhf5X7eqA"
        res = get_livestreaming_details(video_id)
