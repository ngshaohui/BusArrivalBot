from utils.custom_typings import BusStop

from .common import format_result


def bus_stop_search_msg(possible_stops: list[BusStop], page: int = 0) -> str:
    """
    display list of stops matching search query
    """
    if len(possible_stops) == 0:
        return "No bus stops match the search query"

    # list number of results
    msg = ""
    if len(possible_stops) > 1:
        msg += f"{len(possible_stops)} bus stops match "
    else:
        msg = "1 bus stop matches "
    msg += "the search query\n"

    # iterate through each stop
    start_idx = page * 20
    end_idx = min((page + 1) * 20, len(possible_stops))
    for idx in range(start_idx, end_idx):
        msg += f"\n{idx + 1}. {format_result(possible_stops[idx])}"

    # show page number
    if len(possible_stops) > 20:
        msg += f"\n\nPage {page + 1} of {len(possible_stops) // 20 + 1}"
    return msg
