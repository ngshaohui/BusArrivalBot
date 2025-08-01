import unittest
from format_message import bus_stop_search_msg, next_bus_msg
from custom_typings import BusStop, BusInfo

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

BUS_123: list[BusInfo] = [
    {
        "ServiceNo": "123",
        "Operator": "SBST",
        "NextBus": {
            "OriginCode": "10009",
            "DestinationCode": "14539",
            "EstimatedArrival": "2025-01-08T23:59:14+08:00",
            "Monitored": 1,
            "Latitude": "1.2747233333333332",
            "Longitude": "103.823044",
            "VisitNumber": "1",
            "Load": "SEA",
            "Feature": "WAB",
            "Type": "SD",
        },
        "NextBus2": {
            "OriginCode": "10009",
            "DestinationCode": "14539",
            "EstimatedArrival": "2025-01-09T00:20:54+08:00",
            "Monitored": 1,
            "Latitude": "1.302967",
            "Longitude": "103.83563433333333",
            "VisitNumber": "1",
            "Load": "SEA",
            "Feature": "WAB",
            "Type": "SD",
        },
        "NextBus3": {
            "OriginCode": "",
            "DestinationCode": "",
            "EstimatedArrival": "",
            "Monitored": 0,
            "Latitude": "",
            "Longitude": "",
            "VisitNumber": "",
            "Load": "",
            "Feature": "",
            "Type": "",
        },
    }
]


class TestBusSearch(unittest.TestCase):
    def test_no_search_results(self):
        msg = bus_stop_search_msg([])
        expected_str = "0 Bus stops matching the search query\n\n"
        self.assertEqual(msg, expected_str)

    def test_one_search_result(self):
        msg = bus_stop_search_msg(STOPS[:1])
        expected_str = """1 Bus stop matching the search query

/14519 Resorts World Sentosa"""
        self.assertEqual(msg, expected_str)

    def test_multiple_search_results(self):
        msg = bus_stop_search_msg(STOPS)
        expected_str = """6 Bus stops matching the search query

/14519 Resorts World Sentosa
/45029 Opp Heavy Veh Pk
/45359 Blk 790
/59009 Yishun Int
/44539 Lot 1/Choa Chu Kang Stn
/46119 Marsiling CC"""
        self.assertEqual(msg, expected_str)


class TestBusArrival(unittest.TestCase):
    def test_arrival(self):
        msg = next_bus_msg(STOPS[0], BUS_123, 1736351595)
        expected_str = """Resorts World Sentosa | 14519

123
5 min    |    27 min    |    N.A."""
        self.assertEqual(msg, expected_str)


if __name__ == "__main__":
    unittest.main()
