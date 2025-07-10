import random
import unittest
from bus_stops import nearest_stops_utility
from custom_typings import BusStop

STOPS: list[BusStop] = [
    {
        "BusStopCode": "14519",
        "RoadName": "Sentosa Gateway",
        "Description": "Resorts World Sentosa",
        "Latitude": 1.25352193438281,
        "Longitude": 103.82570322127442
    },
    {
        "BusStopCode": "45029",  # closest
        "RoadName": "Woodlands Rd",
        "Description": "Opp Heavy Veh Pk",
        "Latitude": 1.39303959514259,
        "Longitude": 103.75414864750223
    },
    {
        "BusStopCode": "45359",
        "RoadName": "Choa Chu Kang Nth 6",
        "Description": "Blk 790",
        "Latitude": 1.39618571003148,
        "Longitude": 103.74944608386802
    },
    {
        "BusStopCode": "59009",
        "RoadName": "Yishun Ave 2",
        "Description": "Yishun Int",
        "Latitude": 1.4284,
        "Longitude": 103.8360975
    },
    {
        "BusStopCode": "44539",
        "RoadName": "Choa Chu Kang Ave 4",
        "Description": "Lot 1/Choa Chu Kang Stn",
        "Latitude": 1.38463078337388,
        "Longitude": 103.74502387945829
    },
    {
        "BusStopCode": "46119",
        "RoadName": "Admiralty Rd",
        "Description": "Marsiling CC",
        "Latitude": 1.44101545973486,
        "Longitude": 103.77252382232057
    }
]
COORD = (1.397894, 103.7505486)
NEAREST_STOP_CODES = [
    '45359',
    '45029',
    '44539',
    '46119',
    '59009'
]


class TestGetNearestStop(unittest.TestCase):

    def test_shuffled(self):
        for _ in range(10):
            random.shuffle(STOPS)
            get_nearest_stops, _, _ = nearest_stops_utility(STOPS)
            nearest_stops = get_nearest_stops(COORD, 5)
            stop_codes = list(map(lambda x: x["BusStopCode"], nearest_stops))
            self.assertEqual(stop_codes, NEAREST_STOP_CODES)


if __name__ == '__main__':
    unittest.main()
