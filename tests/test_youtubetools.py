import unittest
from unittest import TestCase
from ..youtubetools import (get_upcoming_livestreams,
                            get_livestreaming_details)


class Test(TestCase):
    # @unittest.skip
    def test_get_upcoming_livestreams(self):
        channel_id = "UCJEwPH-wbOTa341mZyJ9NSw"
        ls = get_upcoming_livestreams(channel_id)
        print(ls)

    # @unittest.skip
    def test_get_livestreaming_details(self):
        video_id = "eKfhf5X7eqA"
        res = get_livestreaming_details(video_id)
