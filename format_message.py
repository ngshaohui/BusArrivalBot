from functools import partial

from bus_arrival import get_arrival_time_mins
from custom_typings import BusInfo, BusStop

# TODO need to refer to documentation on how to serve this information in a standardized manner
# TODO test


def bus_arrivals_msg(bus: BusInfo, cur_unix_time: int) -> str:
    '''
    TODO describe
    '''
    next_bus = get_arrival_time(
        bus["NextBus"]["EstimatedArrival"], cur_unix_time)
    next_bus2 = get_arrival_time(
        bus["NextBus2"]["EstimatedArrival"], cur_unix_time)
    next_bus3 = get_arrival_time(
        bus["NextBus3"]["EstimatedArrival"], cur_unix_time)

    return f'''{bus["ServiceNo"]}
{next_bus}    |    {next_bus2}    |    {next_bus3}'''


def get_arrival_time(arrival_time: str, cur_unix_time: int) -> str:
    '''
    get human readable estimated arrival time
    '''
    if arrival_time == '':
        return 'N.A.'
    arrival_time_mins = get_arrival_time_mins(arrival_time, cur_unix_time)
    if arrival_time_mins < 1:
        return 'Arr.'
    return f'{arrival_time_mins} min'


def next_bus_msg(
    bus_stop: BusStop,
    services: list[BusInfo],
    cur_unix_time: int
) -> str:
    '''
    TODO see if it's possible to resolve drilling cur_unix_time
    TODO consider adding legend
    TODO describe
    '''
    title = f"{bus_stop['Description']} | {bus_stop['BusStopCode']}"
    if len(services) == 0:
        return f'{title}\n\nNo service information'

    # use partial to repeatedly pass the same argument cur_unix_time into the bus_arrivals_msg
    # while iterating through list of busses in services
    arrivals = map(partial(bus_arrivals_msg, cur_unix_time=cur_unix_time),
                   services)
    arrivals_text = '\n\n'.join(arrivals)
    return f'{title}\n\n{arrivals_text}'


def __format_result(bus_stop: BusStop) -> str:
    return f"/{bus_stop['BusStopCode']} {bus_stop['Description']}"


def bus_stop_search_msg(possible_stops: list[BusStop]) -> str:
    """
    display list of stops matching search query
    """
    title = f"{len(possible_stops)} Bus stop{"" if len(
        possible_stops) == 1 else "s"} matching the search query"
    stops = map(__format_result, possible_stops)
    stops_text = '\n'.join(stops)
    return f"{title}\n\n{stops_text}"


def bus_route_msg(bus_number: str, stops: list[BusStop]) -> str:
    """
    display list of stops within a bus route
    """
    title = f"Route for bus {bus_number}"
    stops = map(__format_result, stops)
    stops_text = '\n'.join(stops)
    return f"{title}\n\n{stops_text}"
