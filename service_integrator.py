"""
composes functions to give enhanced output
"""
from typing import Callable

from custom_typings import BusRoute, BusStop
from bus_route import bus_route_utility
from bus_stops import nearest_stops_utility

type GetRouteStops = Callable[[str, int], list[BusStop] | None]


def init_integrator(
        bus_routes: list[BusRoute],
        bus_stops: list[BusStop]
):
    # stops
    (get_nearest_stops,
     get_stop_info,
     search_possible_stops) = nearest_stops_utility(bus_stops)

    # routes
    get_bus_route = bus_route_utility(bus_routes)

    def get_route_stops(bus_number: str, direction: int) -> list[BusStop] | None:
        route = get_bus_route(bus_number, direction)

        if route is None:
            # possible that route 2 does not exist
            route = get_bus_route(bus_number, 1)
        if route is None:
            return None

        route_stops = map(get_stop_info, route)
        return [route for route in route_stops if route is not None]

    return (
        get_nearest_stops,
        get_stop_info,
        search_possible_stops,
        get_route_stops
    )
