# Run this script to get an updated routes.json

import datetime
import json
import logging

import httpx
from decouple import config

from utils.checksum import get_dict_list_checksum
from utils.custom_typings import BusRoute

logger = logging.getLogger(__name__)

URL_GET_ALL_ROUTES = "https://datamall2.mytransport.sg/ltaodataservice/BusRoutes"


def fetch_routes() -> list[BusRoute]:
    all_routes: list[BusRoute] = []  # store all the stops in this array
    skips = 0  # use skips since API can only return 500 results at once

    # Build query string
    headers = {"AccountKey": config("ACCOUNT_KEY", cast=str)}

    while True:
        res = httpx.get(f"{URL_GET_ALL_ROUTES}?$skip={skips}", headers=headers)
        json_data = res.json()
        if not json_data["value"]:  # break loop when resulting json is empty
            break
        fetched_all_stops: list[BusRoute] = json_data["value"]
        all_routes += fetched_all_stops
        skips += 500
    return all_routes


def run() -> list[BusRoute]:
    routes = fetch_routes()
    checksum = get_dict_list_checksum(routes)
    logger.info(f"Fetched {len(routes)} bus routes (checksum: {checksum})")
    return routes


def main():
    routes = run()
    checksum = get_dict_list_checksum(routes)
    cur_timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    with open("bus_routes.json", "w") as outfile:
        json.dump(
            {
                "checksum": checksum,
                "created_at": cur_timestamp,
                "bus_routes": routes,
            },
            outfile,
        )


if __name__ == "__main__":
    main()
