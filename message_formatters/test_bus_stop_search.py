from utils.custom_typings import BusStop

from .bus_stop_search import bus_stop_search_msg

# 21 stops
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
    {
        "BusStopCode": "97049",
        "RoadName": "Upp Changi Rd Nth",
        "Description": "Changi Prison",
        "Latitude": 1.35817903735465,
        "Longitude": 103.96973879358464,
    },
    {
        "BusStopCode": "19091",
        "RoadName": "Dover Ave",
        "Description": "S'pore Poly",
        "Latitude": 1.30739277801307,
        "Longitude": 103.78208222199827,
    },
    {
        "BusStopCode": "19099",
        "RoadName": "Dover Ave",
        "Description": "Opp S'pore Poly",
        "Latitude": 1.30697118032996,
        "Longitude": 103.78191236221397,
    },
    {
        "BusStopCode": "20011",
        "RoadName": "AYE",
        "Description": "Blk 506",
        "Latitude": 1.31308624553797,
        "Longitude": 103.76128731220228,
    },
    {
        "BusStopCode": "20019",
        "RoadName": "AYE",
        "Description": "Blk 431",
        "Latitude": 1.31357611099308,
        "Longitude": 103.7615108330155,
    },
    {
        "BusStopCode": "20021",
        "RoadName": "AYE",
        "Description": "NEWest",
        "Latitude": 1.31675923723731,
        "Longitude": 103.75788959223745,
    },
    {
        "BusStopCode": "20029",
        "RoadName": "AYE",
        "Description": "Opp NEWest",
        "Latitude": 1.31772833949651,
        "Longitude": 103.75767989744158,
    },
    {
        "BusStopCode": "20031",
        "RoadName": "AYE",
        "Description": "The Infiniti",
        "Latitude": 1.32055987103977,
        "Longitude": 103.75464677812963,
    },
    {
        "BusStopCode": "20039",
        "RoadName": "AYE",
        "Description": "Opp The Infiniti",
        "Latitude": 1.32102499760642,
        "Longitude": 103.75471510655738,
    },
    {
        "BusStopCode": "20051",
        "RoadName": "AYE",
        "Description": "Cycle & Carriage",
        "Latitude": 1.32258708167298,
        "Longitude": 103.74754428861822,
    },
    {
        "BusStopCode": "20059",
        "RoadName": "AYE",
        "Description": "Opp Cycle & Carriage",
        "Latitude": 1.32332108750232,
        "Longitude": 103.74769351004639,
    },
    {
        "BusStopCode": "32071",
        "RoadName": "Lim Chu Kang Rd",
        "Description": "Aft Track 13",
        "Latitude": 1.4160246040166,
        "Longitude": 103.70056776202736,
    },
    {
        "BusStopCode": "32081",
        "RoadName": "Lim Chu Kang Rd",
        "Description": "Sg Gedong Camp",
        "Latitude": 1.41744631606558,
        "Longitude": 103.70120361125713,
    },
    {
        "BusStopCode": "32089",
        "RoadName": "Lim Chu Kang Rd",
        "Description": "Aft Sg Gedong Camp",
        "Latitude": 1.41681891211204,
        "Longitude": 103.7010851003633,
    },
    {
        "BusStopCode": "32121",
        "RoadName": "Lim Chu Kang Rd",
        "Description": "Aft Old Choa Chu Kang Rd",
        "Latitude": 1.37292105,
        "Longitude": 103.6851701,
    },
]


def test_no_search_results():
    msg = bus_stop_search_msg([])
    expected_str = "No bus stops match the search query"
    assert msg == expected_str


def test_one_search_result():
    msg = bus_stop_search_msg(STOPS[:1])
    expected_str = """1 bus stop matches the search query

1. /14519 Resorts World Sentosa"""
    assert msg == expected_str


def test_single_page_search_results():
    msg = bus_stop_search_msg(STOPS[:20])
    expected_str = """20 bus stops match the search query

1. /14519 Resorts World Sentosa
2. /45029 Opp Heavy Veh Pk
3. /45359 Blk 790
4. /59009 Yishun Int
5. /44539 Lot 1/Choa Chu Kang Stn
6. /46119 Marsiling CC
7. /97049 Changi Prison
8. /19091 S'pore Poly
9. /19099 Opp S'pore Poly
10. /20011 Blk 506
11. /20019 Blk 431
12. /20021 NEWest
13. /20029 Opp NEWest
14. /20031 The Infiniti
15. /20039 Opp The Infiniti
16. /20051 Cycle & Carriage
17. /20059 Opp Cycle & Carriage
18. /32071 Aft Track 13
19. /32081 Sg Gedong Camp
20. /32089 Aft Sg Gedong Camp"""
    assert msg == expected_str


def test_2_page_search_results():
    msg = bus_stop_search_msg(STOPS)
    print(msg)
    expected_str = """21 bus stops match the search query

1. /14519 Resorts World Sentosa
2. /45029 Opp Heavy Veh Pk
3. /45359 Blk 790
4. /59009 Yishun Int
5. /44539 Lot 1/Choa Chu Kang Stn
6. /46119 Marsiling CC
7. /97049 Changi Prison
8. /19091 S'pore Poly
9. /19099 Opp S'pore Poly
10. /20011 Blk 506
11. /20019 Blk 431
12. /20021 NEWest
13. /20029 Opp NEWest
14. /20031 The Infiniti
15. /20039 Opp The Infiniti
16. /20051 Cycle & Carriage
17. /20059 Opp Cycle & Carriage
18. /32071 Aft Track 13
19. /32081 Sg Gedong Camp
20. /32089 Aft Sg Gedong Camp

Page 1 of 2"""
    assert msg == expected_str
