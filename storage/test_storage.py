"""
https://www.sqlite.org/inmemorydb.html
"""

import sqlite3
import unittest
from .adapter import StorageUtility
from .initialize import init


class TestStorage(unittest.TestCase):
    def setUp(self):
        con = sqlite3.connect("file::memory:", uri=True)
        init(con)
        self.storage_utility = StorageUtility(con)

    def test_save_0_stops(self):
        """
        add 0 stops
        """
        self.storage_utility.save_stops(123456, [])
        stops = self.storage_utility.get_saved_stops(123456)
        self.assertEqual(stops, [])

    def test_save_1_stop(self):
        """
        add 1 stop
        """
        self.storage_utility.save_stops(123456, ["123456"])
        stops = self.storage_utility.get_saved_stops(123456)
        self.assertEqual(stops, ["123456"])

    def test_update_stop(self):
        """
        add 1 stop and update
        """
        self.storage_utility.save_stops(123456, ["123456"])
        self.storage_utility.save_stops(123456, ["222", "333", "444"])
        stops = self.storage_utility.get_saved_stops(123456)
        self.assertEqual(stops, ["222", "333", "444"])

    def test_nonexistent_user(self):
        """
        add 1 stop
        """
        self.storage_utility.save_stops(123456, ["123456"])
        stops = self.storage_utility.get_saved_stops(999111)
        self.assertEqual(stops, [])

    def test_check_user_exists(self):
        """
        check if user exists
        """
        self.storage_utility.save_stops(123456, [])
        self.assertTrue(self.storage_utility.check_user_exists(123456))
        self.assertFalse(self.storage_utility.check_user_exists(999111))

    def test_add_and_retrieve_stop(self):
        """
        add one stop to a list of empty stops and retrieve it
        """
        self.storage_utility.add_stop(123456, "42012")
        stops = self.storage_utility.get_saved_stops(123456)
        self.assertEqual(stops, ["42012"])


if __name__ == "__main__":
    unittest.main()
