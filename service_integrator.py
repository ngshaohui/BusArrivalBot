"""
composes functions to give enhanced output
"""
from typing import Callable

from custom_typings import BusRoute, BusStop
from bus_route import bus_route_utility
from bus_stops import nearest_stops_utility

type GetRouteStops = Callable[[str, int], list[BusStop] | None]


class ServiceIntegrator:
    def __init__(self, bus_routes: list[BusRoute], bus_stops: list[BusStop]) -> None:
        self.refresh(bus_routes, bus_stops)

    def get_route_stops(self, bus_number: str, direction: int) -> list[BusStop] | None:
        route = self.get_bus_route(bus_number, direction)

        if route is None:
            # possible that route 2 does not exist
            route = self.get_bus_route(bus_number, 1)
        if route is None:
            return None

        route_stops = map(self.get_stop_info, route)
        return [route for route in route_stops if route is not None]

    def refresh(self, bus_routes: list[BusRoute], bus_stops: list[BusStop]) -> None:
        """update functions"""
        self.get_bus_route = bus_route_utility(bus_routes)
        (self.get_nearest_stops,
         self.get_stop_info,
         self.search_possible_stops) = nearest_stops_utility(bus_stops)
