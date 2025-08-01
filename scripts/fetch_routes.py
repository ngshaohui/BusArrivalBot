# Run this script to get an updated routes.json

from functools import reduce
import hashlib
import json
import requests

from decouple import config

from custom_typings import AllBusRoutes, BusRoute

URL_GET_ALL_ROUTES = "https://datamall2.mytransport.sg/ltaodataservice/BusRoutes"


def get_route_hash(stop: BusRoute) -> bytes:
    """
    calculate hash digest from a string
    """
    msg = hashlib.sha3_256()
    str_values = map(lambda x: str(x).encode(), stop.values())
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
    stop_hash_bytes_ls = list(map(lambda x: get_route_hash(x), stops))
    checksum_bytes = reduce(xor_bytes, stop_hash_bytes_ls)
    return checksum_bytes.hex()


def fetch_routes() -> list[BusRoute]:
    all_routes: list[BusRoute] = []  # store all the stops in this array
    skips = 0  # use skips since API can only return 500 results at once

    # Build query string
    headers = {"AccountKey": config("ACCOUNT_KEY")}

    while True:
        res = requests.get(f"{URL_GET_ALL_ROUTES}?$skip={skips}", headers=headers)
        json_data = res.json()
        if not json_data["value"]:  # break loop when resulting json is empty
            break
        fetched_all_stops: list[BusRoute] = json_data["value"]
        all_routes += fetched_all_stops
        skips += 500
    return all_routes


def run():
    routes = fetch_routes()
    all_routes: AllBusRoutes = {
        "checksum": bus_routes_checksum(routes),
        "bus_routes": routes,
    }

    return all_routes


def main():
    with open("bus_routes.json", "w") as outfile:
        json.dump(run(), outfile)


if __name__ == "__main__":
    main()
