from typing import TypedDict


type Coordinate = tuple[int, int]
type TimestampISO8601 = str  # "2024-11-26T22:04:48+08:00"


class BusStop(TypedDict):
    BusStopCode: str
    RoadName: str
    Description: str
    Latitude: str
    Longitude: str


class NextBusInfo(TypedDict):
    EstimatedArrival: TimestampISO8601
    Load: str
    Feature: str
    Type: str


class BusInfo(TypedDict):
    ServiceNo: str
    NextBus: NextBusInfo
    NextBus2: NextBusInfo
    NextBus3: NextBusInfo


class BusArrivalServiceResponse(TypedDict):
    Services: list[BusInfo]


class AllBusStops(TypedDict):
    bus_stops: list[BusStop]
    checksum: str
