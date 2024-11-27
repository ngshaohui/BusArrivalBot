# Run this script to get an updated all_stops.json
# TODO have some form of message to indicate how many bus all_stops are there and a checksum for logging

import json
import requests
from decouple import config

from custom_typings import BusStop

URL_GET_ALL_STOPS = 'https://datamall2.mytransport.sg/ltaodataservice/Busall_stops'


def main():
    all_stops: list[BusStop] = []  # store all the stops in this array
    skips = 0  # use skips since API can only return 500 results at once

    # Build query string
    headers = {'AccountKey': config('ACCOUNT_KEY')}

    while True:
        res = requests.get(f'{URL_GET_ALL_STOPS}?$skip={skips}', headers=headers)
        json_data = res.json()
        if not json_data["value"]:  # break loop when resulting json is empty
            break
        fetched_all_stops: list[BusStop] = json_data["value"]
        all_stops += fetched_all_stops

    with open('all_stops.json', 'w') as outfile:
        json.dump(all_stops, outfile)


if __name__ == "__main__":
    main()
