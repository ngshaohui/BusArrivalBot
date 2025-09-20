from typing import TypedDict


type Coordinate = tuple[float, float]
type TimestampISO8601 = str  # "2024-11-26T22:04:48+08:00"


class BusRoute(TypedDict):
    ServiceNo: str
    Direction: int
    StopSequence: int
    BusStopCode: str
    Distance: int
    WD_FirstBus: str
    WD_LastBus: str
    SAT_FirstBus: str
    SAT_LastBus: str
    SUN_FirstBus: str
    SUN_LastBus: str


class AllBusRoutes(TypedDict):
    bus_routes: list[BusRoute]
    checksum: str


class BusStop(TypedDict):
    BusStopCode: str
    RoadName: str
    Description: str
    Latitude: float
    Longitude: float


class NextBusInfo(TypedDict):
    OriginCode: str
    DestinationCode: str
    EstimatedArrival: TimestampISO8601
    Monitored: int
    Latitude: str
    Longitude: str
    VisitNumber: str
    Load: str
    Feature: str
    Type: str


class BusInfo(TypedDict):
    ServiceNo: str
    Operator: str
    NextBus: NextBusInfo
    NextBus2: NextBusInfo
    NextBus3: NextBusInfo


class BusArrivalServiceResponse(TypedDict):
    Services: list[BusInfo]


class AllBusStops(TypedDict):
    bus_stops: list[BusStop]
    checksum: str
