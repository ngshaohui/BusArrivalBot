# Run this script to get an updated all_stops.json

import hashlib
import json
import logging
from functools import reduce

import requests
from decouple import config

from utils.custom_typings import BusStop

logger = logging.getLogger(__name__)

URL_GET_ALL_STOPS = "https://datamall2.mytransport.sg/ltaodataservice/BusStops"


def get_stop_hash(stop: BusStop) -> bytes:
    """
    calculate hash digest from a string
    """
    msg = hashlib.sha3_256()
    msg.update(stop["BusStopCode"].encode())
    msg.update(stop["Description"].encode())
    msg.update(stop["RoadName"].encode())
    msg.update(str(stop["Latitude"]).encode())
    msg.update(str(stop["Longitude"]).encode())
    return msg.digest()


def xor_bytes(bytes1: bytes, bytes2: bytes) -> bytes:
    return bytes([b1 ^ b2 for b1, b2 in zip(bytes1, bytes2)])


def bus_stops_checksum(stops: list[BusStop]) -> str:
    """
    calculate checksum of list of stops
    """
    # no need to sort first since we rely on xor
    checksum_bytes = reduce(xor_bytes, map(get_stop_hash, stops))
    return checksum_bytes.hex()


def fetch_stops() -> list[BusStop]:
    all_stops: list[BusStop] = []  # store all the stops in this array
    skips = 0  # use skips since API can only return 500 results at once

    # Build query string
    headers = {"AccountKey": config("ACCOUNT_KEY", cast=str)}

    while True:
        res = requests.get(f"{URL_GET_ALL_STOPS}?$skip={skips}", headers=headers)
        json_data = res.json()
        if not json_data["value"]:  # break loop when resulting json is empty
            break
        fetched_all_stops: list[BusStop] = json_data["value"]
        all_stops += fetched_all_stops
        skips += 500
    return all_stops


def run() -> list[BusStop]:
    stops = fetch_stops()
    checksum = bus_stops_checksum(stops)
    logger.info(f"Fetched {len(stops)} bus stops (checksum: {checksum})")
    return stops


def main():
    stops = run()
    with open("bus_stops.json", "w") as outfile:
        json.dump(stops, outfile)


if __name__ == "__main__":
    main()
