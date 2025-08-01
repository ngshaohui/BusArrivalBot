# workaround: pylance does not resolve cKDTree correctly
from scipy.spatial import cKDTree as KDTree  # type: ignore[attr-defined]

from typing import Callable, Optional
from bus_stop_search_map import transform_query_token
from custom_typings import BusStop, Coordinate

type GetNearestStops = Callable[[Coordinate, Optional[int]], list[BusStop]]
type GetStopInfo = Callable[[str], BusStop | None]
type SearchPossibleStops = Callable[[list[str]], list[BusStop]]


def nearest_stops_utility(
    stops: list[BusStop],
) -> tuple[GetNearestStops, GetStopInfo, SearchPossibleStops]:
    """
    TODO description
    TODO usage instructions
    """
    # convert [{"Latitude": 1, "Longitude": 130}] -> [(1, 130)]
    stop_coordinates = tuple(
        map(lambda stop: (stop["Latitude"], stop["Longitude"]), stops)
    )
    kd_tree = KDTree(stop_coordinates)

    def get_nearest_stops(
        coord: Coordinate, num_stops: Optional[int] = 3
    ) -> list[BusStop]:
        _, nd_indexes = kd_tree.query([coord], k=num_stops)
        # convert numpy 2d array (with only 1 row) to list of integers
        # numpy_ndarray -> [[1, 2, 3]] -> [1, 2, 3]
        indexes = nd_indexes.tolist()[0]
        # indexes is type Any since it is either (1) an integer or (2) array of integers
        # should always be array of integers since we always(?) query for multiple stops
        nearest_stops = list(map(lambda x: stops[x], indexes))
        return nearest_stops

    # create dictionary with BusStopCode as key and BusStop as value
    stops_map = dict(zip(map(lambda x: x["BusStopCode"], stops), stops))

    def get_stop_info(bus_stop_code: str) -> BusStop | None:
        """
        TODO description
        """
        if bus_stop_code not in stops_map:
            return None
        return stops_map[bus_stop_code]

    def create_token_map(stops: list[BusStop]) -> dict[str, set[str]]:
        """
        create map of word tokens to BusStopCodes
        """
        token_map: dict[str, set[str]] = {}
        for stop in stops:
            tokens = stop["Description"].lower().split()

            for token in tokens:
                if token not in token_map:
                    # create set if it does not already exist
                    token_map[token] = set()
                token_map[token].add(stop["BusStopCode"])

        return token_map

    token_map = create_token_map(stops)

    def search_possible_stops(query: list[str]) -> list[BusStop]:
        """
        get a list of bus stops that match a search query
        """
        query_tokens = map(lambda x: x.lower(), query)
        m_query_tokens = map(transform_query_token, query_tokens)
        stop_ids_set: set[str] = set()

        for query_token in m_query_tokens:
            if query_token in token_map:
                if len(stop_ids_set) == 0:
                    # populate empty set
                    stop_ids_set.update(token_map[query_token])
                else:
                    stop_ids_set = set.intersection(
                        stop_ids_set, token_map[query_token]
                    )

        potential_bus_stops = map(get_stop_info, stop_ids_set)
        bus_stops = [stop for stop in potential_bus_stops if stop is not None]
        # TODO sort
        return bus_stops

    return (get_nearest_stops, get_stop_info, search_possible_stops)
