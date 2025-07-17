"""
search for bus stops within a route
"""
from typing import Callable

from custom_typings import BusRoute

type GetBusRoute = Callable[[str, int], list[str] | None]


def bus_route_utility(bus_routes: list[BusRoute]) -> GetBusRoute:
    # {"67": ["44009", "44461", "44469", "44009"]}
    bus_route_map: dict[tuple[str, int], list[str]] = {}

    for route in bus_routes:
        service_number = route['ServiceNo']
        direction = route['Direction']
        service = (service_number, direction)
        if service not in bus_route_map:
            bus_route_map[service] = []
        bus_route_map[service].append(route['BusStopCode'])

    def get_bus_route(bus_number: str, direction: int) -> list[str] | None:
        """
        search for bus stops within a route

        returns a list of BusStopCode
        """
        return bus_route_map.get((bus_number, direction), None)

    return get_bus_route
