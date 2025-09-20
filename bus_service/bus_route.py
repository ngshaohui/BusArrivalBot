"""
search for bus stops within a route
"""

from typing import Callable

from utils.custom_typings import BusRoute, BusStop

type GetBusRoute = Callable[[str, int], list[BusStop] | None]


def bus_route_utility(
    bus_routes: list[BusRoute], get_stop_info: Callable[[str], BusStop | None]
) -> GetBusRoute:
    # {"67": ["44009", "44461", "44469", "44009"]}
    bus_route_map: dict[tuple[str, int], list[str]] = {}

    for route in bus_routes:
        service_number = route["ServiceNo"]
        direction = route["Direction"]
        service = (service_number, direction)
        if service not in bus_route_map:
            bus_route_map[service] = []
        bus_route_map[service].append(route["BusStopCode"])

    def __get_bus_route(bus_number: str, direction: int) -> list[str] | None:
        """
        search for bus stops within a route

        returns a list of BusStopCode
        """
        return bus_route_map.get((bus_number, direction), None)

    def get_route_stops(bus_number: str, direction: int) -> list[BusStop] | None:
        route = __get_bus_route(bus_number, direction)

        if route is None:
            # possible that route 2 does not exist
            route = __get_bus_route(bus_number, 1)
        if route is None:
            return None

        route_stops = map(get_stop_info, route)
        return [route for route in route_stops if route is not None]

    return get_route_stops
