# Run this script to get an updated stops.json

import json
import requests

from credentials import ACCOUNTKEY

def sortLong(item):
    return item["Longitude"]

def sortLat(item):
    return item["Latitude"]

def main():
    target = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip='
    stops = [] #store all the stops in this array
    skips = 0

    #Build query string
    headers = { 'AccountKey': ACCOUNTKEY,
    'accept': 'application/json'}

    while True:
        #use skips since API can only return 50 results at once
        r = requests.get(target + str(skips), headers = headers)
        r = r.json()
        if not r["value"]: #break loop when resulting json is empty
            break
        stops += r["value"] #append to array of stops
        skips += 50

    sortedLong = sorted(stops, key=sortLong)
    sortedLat = sorted(stops, key=sortLat)

    data = {}
    #data["unsorted"] = stops
    data["longSorted"] = sortedLong
    data["latSorted"] = sortedLat

    with open('stops.json', 'w') as outfile:
        json.dump(data, outfile)

if __name__ == "__main__":
    main()
