from datetime import datetime
import time
from typing import NamedTuple

from decouple import config
import requests

from custom_typings import BusArrivalServiceResponse, BusInfo, TimestampISO8601

URL_GET_ARRIVING_BUSSES = 'https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival'


class BusInfoCacheItem(NamedTuple):
    retrieved: int
    busses: list[BusInfo]


# custom cache implementation
CACHE_EXPIRY = 20  # seconds
type CacheLayer = dict[str, BusInfoCacheItem]
__bus_info_cache: CacheLayer = {}


def get_arriving_busses(bus_stop_code: str) -> list[BusInfo]:
    unix_time_now = int(time.time())

    # cache hit
    if bus_stop_code in __bus_info_cache:
        cached_result = __bus_info_cache[bus_stop_code]
        # check if time is valid
        if unix_time_now - cached_result.retrieved < CACHE_EXPIRY:
            return cached_result.busses

    arriving_busses = fetch_arriving_busses(bus_stop_code)
    # store in cache
    __bus_info_cache[bus_stop_code] = BusInfoCacheItem(
        unix_time_now, arriving_busses)
    return arriving_busses


def fetch_arriving_busses(bus_stop_code: str) -> list[BusInfo]:
    """
    TODO describe
    TODO add try-except to handle non status 200 responses
    TODO add timeout for responses
    """
    params = {'BusStopCode': bus_stop_code}
    headers = {'AccountKey': config('ACCOUNT_KEY')}
    res = requests.get(URL_GET_ARRIVING_BUSSES, headers=headers, params=params)
    json_data: BusArrivalServiceResponse = res.json()
    return json_data['Services']


def get_arrival_time_mins(
        bus_arrival_time: TimestampISO8601,
        cur_unix_time: int
) -> int:
    """
    TODO describe
    """
    dt = datetime.fromisoformat(bus_arrival_time)
    unix_time = int(dt.timestamp())
    time_diff_seconds = max(0, unix_time - cur_unix_time)
    return time_diff_seconds // 60
