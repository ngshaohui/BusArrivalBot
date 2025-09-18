from datetime import datetime

from decouple import config
import requests

from custom_typings import BusArrivalServiceResponse, BusInfo, TimestampISO8601
from lru_cache import LRUCache

URL_GET_ARRIVING_BUSSES = (
    "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"
)

__bus_info_cache = LRUCache[list[BusInfo]](ttl=20, item_limit=100)


def get_arriving_busses(bus_stop_code: str) -> list[BusInfo]:
    arriving_busses = __bus_info_cache.get(bus_stop_code)
    if arriving_busses is None:
        arriving_busses = fetch_arriving_busses(bus_stop_code)
        __bus_info_cache.set(bus_stop_code, arriving_busses)
    return arriving_busses


def fetch_arriving_busses(bus_stop_code: str) -> list[BusInfo]:
    """
    TODO describe
    TODO add try-except to handle non status 200 responses
    TODO add timeout for responses
    """
    params = {"BusStopCode": bus_stop_code}
    headers = {"AccountKey": config("ACCOUNT_KEY")}
    res = requests.get(URL_GET_ARRIVING_BUSSES, headers=headers, params=params)
    json_data: BusArrivalServiceResponse = res.json()
    return json_data["Services"]


def get_arrival_time_mins(
    bus_arrival_time: TimestampISO8601, cur_unix_time: int
) -> int:
    """
    TODO describe
    """
    dt = datetime.fromisoformat(bus_arrival_time)
    unix_time = int(dt.timestamp())
    time_diff_seconds = max(0, unix_time - cur_unix_time)
    return time_diff_seconds // 60
