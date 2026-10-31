from utils.custom_typings import BusInfo, BusStop, UserSettings

from .bus_arrival import bus_arrival_sequence, next_bus_msg

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

STOP_14519: list[BusInfo] = [
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

STOP_45029: list[BusInfo] = [
    {
        "ServiceNo": "170",
        "Operator": "SBST",
        "NextBus": {
            "OriginCode": "46239",
            "DestinationCode": "01109",
            "EstimatedArrival": "2026-10-30T20:16:05+08:00",
            "Monitored": 1,
            "Latitude": "1.4099495",
            "Longitude": "103.755882",
            "VisitNumber": "1",
            "Load": "SDA",
            "Feature": "WAB",
            "Type": "SD",
        },
        "NextBus2": {
            "OriginCode": "46239",
            "DestinationCode": "01109",
            "EstimatedArrival": "2026-10-30T20:43:32+08:00",
            "Monitored": 1,
            "Latitude": "1.4497456666666666",
            "Longitude": "103.77011316666666",
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
    },
    {
        "ServiceNo": "178",
        "Operator": "SMRT",
        "NextBus": {
            "OriginCode": "46009",
            "DestinationCode": "22009",
            "EstimatedArrival": "2026-10-30T20:20:58+08:00",
            "Monitored": 1,
            "Latitude": "1.4268398333333332",
            "Longitude": "103.76316283333334",
            "VisitNumber": "1",
            "Load": "SEA",
            "Feature": "WAB",
            "Type": "SD",
        },
        "NextBus2": {
            "OriginCode": "46009",
            "DestinationCode": "22009",
            "EstimatedArrival": "2026-10-30T20:35:44+08:00",
            "Monitored": 1,
            "Latitude": "1.4371651666666667",
            "Longitude": "103.78258566666666",
            "VisitNumber": "1",
            "Load": "SEA",
            "Feature": "WAB",
            "Type": "SD",
        },
        "NextBus3": {
            "OriginCode": "46009",
            "DestinationCode": "22009",
            "EstimatedArrival": "2026-10-30T20:54:02+08:00",
            "Monitored": 0,
            "Latitude": "0.0",
            "Longitude": "0.0",
            "VisitNumber": "1",
            "Load": "SEA",
            "Feature": "WAB",
            "Type": "SD",
        },
    },
    {
        "ServiceNo": "925",
        "Operator": "SMRT",
        "NextBus": {
            "OriginCode": "47009",
            "DestinationCode": "44009",
            "EstimatedArrival": "2026-10-30T20:16:02+08:00",
            "Monitored": 1,
            "Latitude": "1.4058421666666667",
            "Longitude": "103.75526866666667",
            "VisitNumber": "1",
            "Load": "SEA",
            "Feature": "WAB",
            "Type": "SD",
        },
        "NextBus2": {
            "OriginCode": "47009",
            "DestinationCode": "44009",
            "EstimatedArrival": "2026-10-30T20:29:18+08:00",
            "Monitored": 1,
            "Latitude": "1.4385706666666667",
            "Longitude": "103.743009",
            "VisitNumber": "1",
            "Load": "SEA",
            "Feature": "WAB",
            "Type": "SD",
        },
        "NextBus3": {
            "OriginCode": "47009",
            "DestinationCode": "44009",
            "EstimatedArrival": "2026-10-30T20:45:04+08:00",
            "Monitored": 1,
            "Latitude": "1.4291593333333332",
            "Longitude": "103.76677533333333",
            "VisitNumber": "1",
            "Load": "SEA",
            "Feature": "WAB",
            "Type": "SD",
        },
    },
]


def test_arrival():
    msg = next_bus_msg(STOPS[0], STOP_14519, 1736351595, UserSettings(False, False, 0))
    expected_str = """Resorts World Sentosa | 14519

123
5 min  |  27 min  |  N.A.

Last refreshed 8 Jan 11.53PM"""
    assert msg == expected_str


def test_arrival_multiple_buses():
    msg = next_bus_msg(STOPS[1], STOP_45029, 1793362364, UserSettings(False, False, 0))
    expected_str = """Opp Heavy Veh Pk | 45029

170
3 min  |  30 min  |  N.A.

178
8 min  |  23 min  |  41 min

925
3 min  |  16 min  |  32 min

Last refreshed 30 Oct 8.12PM"""
    assert msg == expected_str


def test_arrival_6_arrival_sequence():
    msg = next_bus_msg(STOPS[1], STOP_45029, 1793362364, UserSettings(False, False, 6))
    expected_str = """Opp Heavy Veh Pk | 45029

925 (3 min) → 170 (3 min) → 178 (8 min) → 925 (16 min) → 178 (23 min) → 170 (30 min)

170
3 min  |  30 min  |  N.A.

178
8 min  |  23 min  |  41 min

925
3 min  |  16 min  |  32 min

Last refreshed 30 Oct 8.12PM"""
    assert msg == expected_str


def test_arrival_sequence():
    msg = bus_arrival_sequence(STOP_14519, 1736351595, UserSettings(False, False, 2))
    expected_str = "123 (5 min) → 123 (27 min)"
    assert msg == expected_str


def test_arrival_sequence_less_bus_services():
    msg = bus_arrival_sequence(STOP_14519, 1736351595, UserSettings(False, False, 3))
    expected_str = "123 (5 min) → 123 (27 min)"
    assert msg == expected_str


def test_arrival_sequence_more_bus_services():
    msg = bus_arrival_sequence(STOP_14519, 1736351595, UserSettings(False, False, 1))
    expected_str = "123 (5 min)"
    assert msg == expected_str
