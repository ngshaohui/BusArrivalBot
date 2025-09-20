"""
composes functions to give enhanced output
"""

from typing import Callable

from utils.custom_typings import BusRoute, BusStop
from .bus_route import bus_route_utility
from .bus_stops import nearest_stops_utility

type GetRouteStops = Callable[[str, int], list[BusStop] | None]


class BusServiceAdapter:
    def __init__(self, bus_stops: list[BusStop], bus_routes: list[BusRoute]) -> None:
        self.refresh(bus_stops, bus_routes)

    def refresh(self, bus_stops: list[BusStop], bus_routes: list[BusRoute]) -> None:
        """update functions"""
        (
            self.get_nearest_stops,
            self.get_stop_info,
            self.search_possible_stops,
        ) = nearest_stops_utility(bus_stops)
        self.get_route_stops = bus_route_utility(bus_routes, self.get_stop_info)
