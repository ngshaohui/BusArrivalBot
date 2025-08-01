import unittest
from bus_arrival import get_arrival_time_mins

UNIX_TIME = 1732635550  # 2024-11-26T23:39:10+08:00


# TODO test different timezones
class TestGetArrivalTimes(unittest.TestCase):
    def test_future1(self):
        time_diff = get_arrival_time_mins("2024-11-26T23:42:58+08:00", UNIX_TIME)
        self.assertEqual(time_diff, 3)

    def test_future2(self):
        time_diff = get_arrival_time_mins("2024-11-26T23:56:10+08:00", UNIX_TIME)
        self.assertEqual(time_diff, 17)

    def test_future3(self):
        time_diff = get_arrival_time_mins("2024-11-26T23:53:59+08:00", UNIX_TIME)
        self.assertEqual(time_diff, 14)

    def test_same(self):
        time_diff = get_arrival_time_mins("2024-11-26T23:39:10+08:00", UNIX_TIME)
        self.assertEqual(time_diff, 0)

    def test_past1(self):
        time_diff = get_arrival_time_mins("2024-11-26T23:39:09+08:00", UNIX_TIME)
        self.assertEqual(time_diff, 0)

    def test_past2(self):
        time_diff = get_arrival_time_mins("2024-11-26T22:53:59+08:00", UNIX_TIME)
        self.assertEqual(time_diff, 0)


if __name__ == "__main__":
    unittest.main()
