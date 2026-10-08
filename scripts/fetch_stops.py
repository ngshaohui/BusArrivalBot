# Run this script to get an updated all_stops.json

import datetime
import json
import logging

import httpx
from decouple import config

from utils.checksum import get_dict_list_checksum
from utils.custom_typings import BusStop

logger = logging.getLogger(__name__)

URL_GET_ALL_STOPS = "https://datamall2.mytransport.sg/ltaodataservice/BusStops"


def fetch_stops() -> list[BusStop]:
    all_stops: list[BusStop] = []  # store all the stops in this array
    skips = 0  # use skips since API can only return 500 results at once

    # Build query string
    headers = {"AccountKey": config("ACCOUNT_KEY", cast=str)}

    while True:
        res = httpx.get(f"{URL_GET_ALL_STOPS}?$skip={skips}", headers=headers)
        json_data = res.json()
        if not json_data["value"]:  # break loop when resulting json is empty
            break
        fetched_all_stops: list[BusStop] = json_data["value"]
        all_stops += fetched_all_stops
        skips += 500
    return all_stops


def run() -> list[BusStop]:
    stops = fetch_stops()
    checksum = get_dict_list_checksum(stops)
    logger.info(f"Fetched {len(stops)} bus stops (checksum: {checksum})")
    return stops


def main():
    stops = run()
    checksum = get_dict_list_checksum(stops)
    cur_timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    with open("bus_stops.json", "w") as outfile:
        json.dump(
            {
                "checksum": checksum,
                "created_at": cur_timestamp,
                "bus_stops": stops,
            },
            outfile,
        )


if __name__ == "__main__":
    main()
