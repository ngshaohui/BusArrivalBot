import re
from collections.abc import Callable
from dataclasses import dataclass, field

from scipy.spatial import KDTree

from utils.checksum import get_dict_list_checksum
from utils.custom_typings import BusStop, Coordinate

from .bus_stop_search_map import transform_query_token

type GetNearestStops = Callable[[Coordinate, int], list[BusStop]]
type GetStopInfo = Callable[[str], BusStop | None]
type SearchPossibleStops = Callable[[list[str]], list[BusStop]]


# TODO: test before using
@dataclass
class BusStopUtility:
    stops: list[BusStop]
    stops_checksum: str = field(init=False)

    stop_coordinates: list[Coordinate] = field(init=False)
    kd_tree: KDTree = field(init=False)
    token_map: dict[str, set[str]] = field(init=False)
    stops_map: dict[str, BusStop] = field(init=False)  # dict[BusStopCode, BusStop]

    def __post_init__(self):
        self.create(self.stops)

    def create(self, stops: list[BusStop]) -> None:
        self.stops = stops
        self.stops_checksum = get_dict_list_checksum(stops)
        self.stop_coordinates = [
            (stop["Latitude"], stop["Longitude"]) for stop in stops
        ]
        self.kd_tree = KDTree(self.stop_coordinates)
        self.token_map = self._create_token_map(stops)
        self.stops_map = {stop["BusStopCode"]: stop for stop in stops}

    def _create_token_map(self, stops: list[BusStop]) -> dict[str, set[str]]:
        """
        create map of word tokens to BusStopCodes
        """
        token_map: dict[str, set[str]] = {}
        for stop in stops:
            tokens = re.split(r"[\s\/\-]", stop["Description"].lower())
            tokens = filter(len, tokens)

            for token in tokens:
                if token not in token_map:
                    # create set if it does not already exist
                    token_map[token] = set()
                token_map[token].add(stop["BusStopCode"])

        return token_map

    def get_nearest_stops(self, coord: Coordinate, num_stops: int = 3) -> list[BusStop]:
        _, nd_indexes = self.kd_tree.query([coord], k=num_stops)
        # convert numpy 2d array (with only 1 row) to list of integers
        # numpy_ndarray -> [[1, 2, 3]] -> [1, 2, 3]
        indexes = nd_indexes.tolist()[0]
        # indexes is type Any since it is either (1) an integer or (2) array of integers
        # should always be array of integers since we always(?) query for multiple stops
        nearest_stops = [self.stops[idx] for idx in indexes]
        return nearest_stops

    def get_stop_info(self, bus_stop_code: str) -> BusStop | None:
        """
        obtain BusStop information for a given bus stop code
        """
        return self.stops_map.get(bus_stop_code)

    def search_possible_stops(self, query: list[str]) -> list[BusStop]:
        """
        get a list of bus stops that match a search query
        """
        query_tokens = (token.lower() for token in query)
        m_query_tokens = map(transform_query_token, query_tokens)
        stop_ids_set: set[str] = set()

        for query_token in m_query_tokens:
            if query_token in self.token_map:
                if len(stop_ids_set) == 0:
                    # populate empty set
                    stop_ids_set.update(self.token_map[query_token])
                else:
                    stop_ids_set = set.intersection(
                        stop_ids_set, self.token_map[query_token]
                    )

        potential_bus_stops = map(self.get_stop_info, stop_ids_set)
        bus_stops = [stop for stop in potential_bus_stops if stop is not None]
        # TODO sort
        return bus_stops


def bus_stop_utility(
    stops: list[BusStop],
) -> tuple[GetNearestStops, GetStopInfo, SearchPossibleStops]:
    """
    TODO description
    TODO usage instructions
    """
    # convert [{"Latitude": 1, "Longitude": 130}] -> [(1, 130)]
    stop_coordinates = [(stop["Latitude"], stop["Longitude"]) for stop in stops]
    kd_tree = KDTree(stop_coordinates)

    def get_nearest_stops(coord: Coordinate, num_stops: int = 3) -> list[BusStop]:
        _, nd_indexes = kd_tree.query([coord], k=num_stops)
        # convert numpy 2d array (with only 1 row) to list of integers
        # numpy_ndarray -> [[1, 2, 3]] -> [1, 2, 3]
        indexes = nd_indexes.tolist()[0]
        # indexes is type Any since it is either (1) an integer or (2) array of integers
        # should always be array of integers since we always(?) query for multiple stops
        nearest_stops = [stops[idx] for idx in indexes]
        return nearest_stops

    # create dictionary with BusStopCode as key and BusStop as value
    stops_map = dict(zip([stop["BusStopCode"] for stop in stops], stops))

    def get_stop_info(bus_stop_code: str) -> BusStop | None:
        """
        obtain BusStop information for a given bus stop code
        """
        return stops_map.get(bus_stop_code)

    def create_token_map(stops: list[BusStop]) -> dict[str, set[str]]:
        """
        create map of word tokens to BusStopCodes
        """
        token_map: dict[str, set[str]] = {}
        for stop in stops:
            tokens = re.split(r"[\s\/\-]", stop["Description"].lower())
            tokens = filter(len, tokens)

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
        query_tokens = (token.lower() for token in query)
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
