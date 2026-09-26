import pytest

from utils.custom_typings import BusStop

from .bus_stops import SearchPossibleStops, bus_stop_utility

STOPS: list[BusStop] = [
    {
        "BusStopCode": "14519",
        "RoadName": "Sentosa Gateway",
        "Description": "Resorts World Sentosa",
        "Latitude": 1.25352193438281,
        "Longitude": 103.82570322127442,
    },
    {
        "BusStopCode": "45029",
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
    {
        "BusStopCode": "83062",
        "RoadName": "Sims Ave East",
        "Description": "Kembangan Stn",
        "Latitude": 1.32096859171096,
        "Longitude": 103.9133277893385,
    },
]


@pytest.fixture
def search_possible_stops():
    _, _, search_possible_stops = bus_stop_utility(STOPS)
    return search_possible_stops


def test_search_single_stop_exact_match(search_possible_stops: SearchPossibleStops):
    stops = search_possible_stops(["Resords", "World", "Sentosa"])
    assert stops == [STOPS[0]]


def test_search_single_stop_partial_match(search_possible_stops: SearchPossibleStops):
    stops = search_possible_stops(["Sentosa"])
    assert stops == [STOPS[0]]


def test_search_multiple_stops(search_possible_stops: SearchPossibleStops):
    stops = search_possible_stops(["stn"])
    assert sorted([stop["BusStopCode"] for stop in stops]) == sorted(
        [STOPS[4]["BusStopCode"], STOPS[6]["BusStopCode"]]
    )


def test_search_keyword_expansion(search_possible_stops: SearchPossibleStops):
    stops = search_possible_stops(["opp", "vehicle", "park"])
    assert stops == [STOPS[1]]


def test_search_multiple_stops_keyword_expansion(
    search_possible_stops: SearchPossibleStops,
):
    stops = search_possible_stops(["station"])
    assert sorted([stop["BusStopCode"] for stop in stops]) == sorted(
        [STOPS[4]["BusStopCode"], STOPS[6]["BusStopCode"]]
    )


def test_search_no_stops(search_possible_stops: SearchPossibleStops):
    stops = search_possible_stops(["changi"])
    assert stops == []


def test_search_mixed_case(search_possible_stops: SearchPossibleStops):
    stops = search_possible_stops(["sEntosA"])
    assert stops == [STOPS[0]]


def test_search_partial_multiple_keywords(search_possible_stops: SearchPossibleStops):
    stops = search_possible_stops(["choa", "kang"])
    assert stops == [STOPS[4]]
