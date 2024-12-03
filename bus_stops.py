from typing import Callable
from custom_typings import BusStop, Coordinate
from scipy.spatial import cKDTree as KDTree

type GetNearestStops = Callable[[str, str], str]
type GetStopInfo = Callable[[str], BusStop | None]


def nearest_stops_utility(
        stops: list[BusStop]
) -> tuple[GetNearestStops, GetStopInfo]:
    """
    TODO description
    TODO usage instructions
    """
    # convert [{"Latitude": 1, "Longitude": 130}] -> [(1, 130)]
    stop_coordinates = tuple(
        map(lambda stop: (stop["Latitude"], stop["Longitude"]), stops))
    kd_tree = KDTree(stop_coordinates)

    def get_nearest_stops(coord: Coordinate, num_stops: int = 3) -> list[BusStop]:
        _, nd_indexes = kd_tree.query([coord], k=num_stops)
        # convert numpy 2d array (with only 1 row) to list of integers
        # numpy_ndarray -> [[1, 2, 3]] -> [1, 2, 3]
        indexes = nd_indexes.tolist()[0]
        # indexes is type Any since it is either (1) an integer or (2) array of integers
        # should always be array of integers since we always(?) query for multiple stops
        nearest_stops = list(map(lambda x: stops[x], indexes))
        return nearest_stops

    # create dictionary with BusStopCode as key and BusStop as value
    stops_map = dict(zip(
        map(lambda x: x["BusStopCode"], stops),
        stops
    ))

    def get_stop_info(bus_stop_code: str) -> BusStop | None:
        """
        TODO description
        """
        if bus_stop_code not in stops_map:
            return None
        return stops_map[bus_stop_code]

    return get_nearest_stops, get_stop_info
