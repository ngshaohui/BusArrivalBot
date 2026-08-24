# Run this script to get an updated routes.json

import hashlib
import json
import logging
from functools import reduce

import requests
from decouple import config

from utils.custom_typings import BusRoute

logger = logging.getLogger(__name__)

URL_GET_ALL_ROUTES = "https://datamall2.mytransport.sg/ltaodataservice/BusRoutes"


def get_route_hash(stop: BusRoute) -> bytes:
    """
    calculate hash digest from a string
    """
    msg = hashlib.sha3_256()
    str_values = (str(attr).encode() for attr in stop.values())
    for val in str_values:
        msg.update(val)
    return msg.digest()


def xor_bytes(bytes1: bytes, bytes2: bytes) -> bytes:
    return bytes([b1 ^ b2 for b1, b2 in zip(bytes1, bytes2)])


def bus_routes_checksum(stops: list[BusRoute]) -> str:
    """
    calculate checksum of list of stops
    """
    # no need to sort first since we rely on xor
    checksum_bytes = reduce(xor_bytes, map(get_route_hash, stops))
    return checksum_bytes.hex()


def fetch_routes() -> list[BusRoute]:
    all_routes: list[BusRoute] = []  # store all the stops in this array
    skips = 0  # use skips since API can only return 500 results at once

    # Build query string
    headers = {"AccountKey": config("ACCOUNT_KEY", cast=str)}

    while True:
        res = requests.get(f"{URL_GET_ALL_ROUTES}?$skip={skips}", headers=headers)
        json_data = res.json()
        if not json_data["value"]:  # break loop when resulting json is empty
            break
        fetched_all_stops: list[BusRoute] = json_data["value"]
        all_routes += fetched_all_stops
        skips += 500
    return all_routes


def run() -> list[BusRoute]:
    routes = fetch_routes()
    checksum = bus_routes_checksum(routes)
    logger.info(f"Fetched {len(routes)} bus routes (checksum: {checksum})")
    return routes


def main():
    routes = run()
    with open("bus_routes.json", "w") as outfile:
        json.dump(routes, outfile)


if __name__ == "__main__":
    main()
