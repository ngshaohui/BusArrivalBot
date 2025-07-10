"""
https://www.sqlite.org/inmemorydb.html
"""

import sqlite3
import unittest
from .adapter import storage_utility_h
from .initialize import init


class TestStorage(unittest.TestCase):
    def setUp(self):
        con = sqlite3.connect("file::memory:", uri=True)
        init(con)
        self.get_saved_stops, self.save_stops = storage_utility_h(con)

    def test_save_1_stop(self):
        """
        add 1 stop
        """
        self.save_stops(123456, ["123456"])
        stops = self.get_saved_stops(123456)
        self.assertEqual(stops, ["123456"])

    def test_update_stop(self):
        """
        add 1 stop and update
        """
        self.save_stops(123456, ["123456"])
        self.save_stops(123456, ["222", "333", "444"])
        stops = self.get_saved_stops(123456)
        self.assertEqual(stops, ["222", "333", "444"])

    def test_nonexistent_user(self):
        """
        add 1 stop
        """
        self.save_stops(123456, ["123456"])
        stops = self.get_saved_stops(999111)
        self.assertEqual(stops, [])


if __name__ == '__main__':
    unittest.main()
