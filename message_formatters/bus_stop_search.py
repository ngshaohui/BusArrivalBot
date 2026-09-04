from utils.custom_typings import BusStop

from .common import format_result


def bus_stop_search_msg(possible_stops: list[BusStop]) -> str:
    """
    display list of stops matching search query
    """
    if len(possible_stops) == 0:
        return "No bus stops match the search query"
    title = f"""Showing {min(20, len(possible_stops))} out of {
        len(possible_stops)
    } bus stop{"" if len(possible_stops) == 1 else "s"} matching the search query"""
    stops = map(format_result, possible_stops[:20])
    stops_text = "\n".join(stops)
    return f"{title}\n\n{stops_text}"
