import random
import unittest

from utils.custom_typings import BusStop
from .fetch_stops import bus_stops_checksum

STOPS: list[BusStop] = [
    {
        "BusStopCode": "14519",
        "RoadName": "Sentosa Gateway",
        "Description": "Resorts World Sentosa",
        "Latitude": 1.25352193438281,
        "Longitude": 103.82570322127442,
    },
    {
        "BusStopCode": "45029",  # closest
        "RoadName": "Woodlands Rd",
        "Description": "Opp Heavy Veh Pk",
        "Latitude": 1.39303959514259,
        "Longitude": 103.75414864750223,
    },
    {
        "BusStopCode": "45359",
        "RoadName": "Choa Chu Kang Nth 6",
        "Description": "Blk 790",
        "Latitude": 1.39618571003148,
        "Longitude": 103.74944608386802,
    },
    {
        "BusStopCode": "59009",
        "RoadName": "Yishun Ave 2",
        "Description": "Yishun Int",
        "Latitude": 1.4284,
        "Longitude": 103.8360975,
    },
    {
        "BusStopCode": "44539",
        "RoadName": "Choa Chu Kang Ave 4",
        "Description": "Lot 1/Choa Chu Kang Stn",
        "Latitude": 1.38463078337388,
        "Longitude": 103.74502387945829,
    },
    {
        "BusStopCode": "46119",
        "RoadName": "Admiralty Rd",
        "Description": "Marsiling CC",
        "Latitude": 1.44101545973486,
        "Longitude": 103.77252382232057,
    },
]

# TODO test for stop attribute changes in one/more of the fields


class TestFetchStopsChecksum(unittest.TestCase):
    def test_shuffled(self):
        hashes: list[str] = []
        for _ in range(10):
            random.shuffle(STOPS)
            hashes.append(bus_stops_checksum(STOPS))
        # ensure all hashes in list are the same
        self.assertEqual(len(set(hashes)), 1)


if __name__ == "__main__":
    unittest.main()
