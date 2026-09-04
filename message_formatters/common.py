from utils.custom_typings import BusStop


def format_result(bus_stop: BusStop) -> str:
    return f"/{bus_stop['BusStopCode']} {bus_stop['Description']}"
