from functools import partial

from bus_arrival import get_arrival_time_mins
from custom_typings import BusInfo, BusStop

# TODO need to refer to documentation on how to serve this information in a standardized manner
# TODO test


def make_bus_arrivals_msg(bus: BusInfo, cur_unix_time: int) -> str:
    '''
    TODO describe
    '''

    return f'''
{bus["ServiceNo"]}
Next: {get_arrival_time(bus["NextBus"]["EstimatedArrival"], cur_unix_time)}
Subsequent: {get_arrival_time(
        bus["NextBus2"]["EstimatedArrival"], cur_unix_time)}
'''


def get_arrival_time(arrival_time: str, cur_unix_time: int) -> str:
    '''
    TODO describe
    '''
    if arrival_time == '':
        return 'N.A.'
    arrival_time_mins = get_arrival_time_mins(arrival_time, cur_unix_time)
    if arrival_time_mins < 1:
        return 'arriving...'
    return f'{arrival_time_mins} min'


def make_next_bus_msg(
    bus_stop: BusStop,
    services: list[BusInfo],
    cur_unix_time: int
) -> str:
    '''
    TODO see if it's possible to resolve drilling cur_unix_time
    TODO consider adding legend
    TODO describe
    '''
    title = f"{bus_stop['BusStopCode']} | {bus_stop['Description']}"
    # use partial to repeatedly pass the same argument cur_unix_time into the make_bus_arrivals_msg
    # while iterating through list of busses in services
    arrivals = map(partial(make_bus_arrivals_msg, cur_unix_time=cur_unix_time),
                   services)
    arrivals_text = ''.join(arrivals)
    return f'{title}\n\n{arrivals_text}'
