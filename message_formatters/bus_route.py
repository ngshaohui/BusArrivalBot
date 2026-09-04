from utils.custom_typings import BusStop

from .common import format_result


def bus_route_msg(bus_number: str, stops: list[BusStop]) -> str:
    """
    display list of stops within a bus route
    """
    title = f"Route for bus {bus_number}"
    stops_text_ls = map(format_result, stops)
    stops_text = "\n".join(stops_text_ls)
    return f"{title}\n\n{stops_text}"
