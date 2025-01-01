"""
search for bus stops within a route
"""
from typing import Callable

from custom_typings import BusRoute

type GetBusRoute = Callable[[str], list[str] | None]


def bus_route_utility(bus_routes: list[BusRoute]) -> GetBusRoute:
    # {"67": ["44009", "44461", "44469", "44009"]}
    bus_route_map: dict[str, list[str]] = {}

    for route in bus_routes:
        service_number = route['ServiceNo']
        if service_number not in bus_route_map:
            bus_route_map[service_number] = []
        bus_route_map[service_number].append(route['BusStopCode'])

    def get_bus_route(bus_number: str) -> list[str] | None:
        """
        search for bus stops within a route

        returns a list of BusStopCode
        """
        return bus_route_map.get(bus_number, None)

    return get_bus_route
