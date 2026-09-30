import datetime
import zoneinfo
from typing import NamedTuple

from bus_service.bus_arrival import get_arrival_time_mins
from utils.custom_typings import BusInfo, BusStop, NextBusInfo, UserSettings

# TODO need to refer to documentation on how to serve this information in a standardized manner

BUS_LOAD = {
    "SEA": "🟢",  # Seats Available
    "SDA": "🟡",  # Standing Available
    "LSD": "🔴",  # Limited Standing
}
BUS_TYPE = {"BD": "BD", "DD": "DD"}


def bus_arrivals_msg(
    bus: BusInfo, cur_unix_time: int, user_settings: UserSettings
) -> str:
    """
    craft message for bus arrival timing estimates for a single bus number
    """
    next_busses = [bus["NextBus"], bus["NextBus2"], bus["NextBus3"]]
    bus_arrivals = [
        f"{get_arrival_time(b['EstimatedArrival'], cur_unix_time)}{get_arrival_load_and_type(b, user_settings)}"
        for b in next_busses
    ]

    return f"{bus['ServiceNo']}\n{'  |  '.join(bus_arrivals)}"


def get_arrival_load_and_type(
    next_bus_info: NextBusInfo, user_settings: UserSettings
) -> str:
    text = ""
    if user_settings.show_load:
        text += BUS_LOAD.get(next_bus_info["Load"], "")
    if user_settings.show_type:
        text += BUS_TYPE.get(next_bus_info["Type"], "")
    return text if len(text) == 0 else f" ({text})"


def get_arrival_time(arrival_time: str, cur_unix_time: int) -> str:
    """
    get human readable estimated arrival time
    """
    if arrival_time == "":
        return "N.A."

    arrival_time_mins = get_arrival_time_mins(arrival_time, cur_unix_time)

    if arrival_time_mins < 1:
        return "Arr."

    return f"{arrival_time_mins} min"


def next_bus_msg(
    bus_stop: BusStop,
    services: list[BusInfo],
    cur_unix_time: int,
    user_settings: UserSettings,
) -> str:
    """
    TODO see if it's possible to resolve drilling cur_unix_time
    TODO sort the bus numbers
    craft message to indicate bus arrival information for a single stop
    """
    title = f"{bus_stop['Description']} | {bus_stop['BusStopCode']}"
    if len(services) == 0:
        return f"{title}\n\nNo service information"

    arrivals = [
        bus_arrivals_msg(bus_service, cur_unix_time, user_settings)
        for bus_service in services
    ]
    arrivals_text = "\n\n".join(arrivals)
    formatted_datetime = datetime.datetime.fromtimestamp(
        cur_unix_time, tz=zoneinfo.ZoneInfo("Asia/Singapore")
    ).strftime("%-d %b %-I.%M%p")

    if user_settings.show_arrival_sequence == True:
        arrival_sequence = bus_arrival_sequence(services, cur_unix_time)
        return f"{title}\n\n{arrival_sequence}\n\n{arrivals_text}\n\nLast refreshed {formatted_datetime}"
    else:
        return f"{title}\n\n{arrivals_text}\n\nLast refreshed {formatted_datetime}"


class BusSequence(NamedTuple):
    arrival_time: str
    bus_service: str


def bus_arrival_sequence(services: list[BusInfo], cur_unix_time: int) -> str:
    buses_in_sequence: list[BusSequence] = []
    for service in services:
        service_no = service["ServiceNo"]

        for bus in ["NextBus", "NextBus2", "NextBus3"]:
            arrival_time = service[bus]["EstimatedArrival"]

            if arrival_time == "":
                continue

            buses_in_sequence.append(BusSequence(arrival_time, service_no))

    buses_in_sequence.sort(key=lambda bus: bus.arrival_time)

    return " → ".join(
        f"{bus[1]} ({get_arrival_time(bus[0], cur_unix_time)})"
        for bus in buses_in_sequence[:3]
    )
