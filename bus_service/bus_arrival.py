import logging
import time
from datetime import datetime

import httpx
from decouple import config

from utils.custom_typings import BusArrivalServiceResponse, BusInfo, TimestampISO8601
from utils.lru_cache import LRUCache

logger = logging.getLogger(__name__)

_last_error_log_time: float = 0
_ERROR_LOG_COOLDOWN = 1800  # 30 minutes

URL_GET_ARRIVING_BUSSES = (
    "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"
)

_bus_info_cache = LRUCache[list[BusInfo]](ttl=20, item_limit=100)


async def get_arriving_busses(bus_stop_code: str) -> list[BusInfo] | None:
    arriving_busses = _bus_info_cache.get(bus_stop_code)
    if arriving_busses is None:
        arriving_busses = await fetch_arriving_busses(bus_stop_code)
        if arriving_busses is not None:
            _bus_info_cache.set(bus_stop_code, arriving_busses)
    return arriving_busses


async def fetch_arriving_busses(bus_stop_code: str) -> list[BusInfo] | None:
    """
    fetch bus arrival timings from the LTA API
    """
    params = {"BusStopCode": bus_stop_code}
    headers = {"AccountKey": config("ACCOUNT_KEY")}
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                URL_GET_ARRIVING_BUSSES, headers=headers, params=params, timeout=10
            )
            res.raise_for_status()
            json_data: BusArrivalServiceResponse = res.json()
            return json_data["Services"]
        except httpx.RequestError as e:
            # throttle error logging to prevent them from flooding logs
            now = time.time()
            global _last_error_log_time
            if now - _last_error_log_time > _ERROR_LOG_COOLDOWN:
                logger.error(f"Failed to fetch bus arrivals {e}")
                _last_error_log_time = now
            return None


def get_arrival_time_mins(
    bus_arrival_time: TimestampISO8601, cur_unix_time: int
) -> int:
    """
    gets human readable arrival time remaining for the bus
    """
    dt = datetime.fromisoformat(bus_arrival_time)
    unix_time = int(dt.timestamp())
    time_diff_seconds = max(0, unix_time - cur_unix_time)
    return time_diff_seconds // 60
