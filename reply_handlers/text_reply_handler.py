import re
import time
from typing import Callable

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bus_stops import GetStopInfo, SearchPossibleStops
from format_message import bus_route_msg, bus_stop_search_msg, next_bus_msg
from reply_handlers.settings_handler import add_stop
from saved_stops import list_saved_stops
from service_integrator import GetRouteStops, ServiceIntegrator
from storage.adapter import StorageUtility
from .inline_buttons import make_change_route_btn, make_refresh_button
from bus_arrival import get_arriving_busses


# 34120
# /29125
REGEX_STOP_CODE = r"\/?(\d{5})"
# 67
# /961M
REGEX_BUS_NUM = r"\/?(\d{1,3}[A-Za-z]?)"
# route 2
# /route 307E
REGEX_ROUTE = r"\/?route\s*(\d{1,3}[A-Za-z]?)?"
# search opp heavy
# /search pei
REGEX_SEARCH = r"\/?search\s*(.*)"
# add 34120
# /add 29125
# add_34343
# /add_12345
REGEX_ADD_STOP = r"\/?add[?:\s*|_](\d{5})"
# list
# /list
REGEX_LIST_SAVED_STOPS = r"\/?list"


def message_handler(
    service_integrator: ServiceIntegrator, storage_utility: StorageUtility
) -> Callable:
    async def reply(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """
        parse all text that the user sends

        this function then sends the request to the specific handler
        """
        if update.message is None or update.message.text is None:
            return
        msg = update.message.text

        if match := re.match(REGEX_STOP_CODE, msg):
            stop_code = match.group(1)
            await bus_stop_code(service_integrator.get_stop_info, update, stop_code)
        elif match := re.match(REGEX_BUS_NUM, msg, re.IGNORECASE):
            bus_number = match.group(1)
            await bus_route(service_integrator.get_route_stops, update, bus_number)
        elif match := re.match(REGEX_ROUTE, msg, re.IGNORECASE):
            bus_number = match.group(1)
            await bus_route(service_integrator.get_route_stops, update, bus_number)
        elif match := re.match(REGEX_SEARCH, msg, re.IGNORECASE):
            query_str = match.group(1)
            query: list[str] = re.split(r"\s", query_str)
            await search(service_integrator.search_possible_stops, update, query)
        elif match := re.match(REGEX_ADD_STOP, msg, re.IGNORECASE):
            stop_code = match.group(1)
            await add_stop(
                storage_utility, service_integrator.get_stop_info, update, stop_code
            )
        elif re.match(REGEX_LIST_SAVED_STOPS, msg, re.IGNORECASE) is not None:
            await list_saved_stops(
                storage_utility, service_integrator.get_stop_info, update
            )
        else:
            # unknown command message
            await unknown_command(update)

    return reply


async def bus_stop_code(
    get_stop_info: GetStopInfo, update: Update, stop_id: str
) -> None:
    """
    reply user with bus arrival information
    """
    if update.message is None:
        return

    # craft message
    stop_info = get_stop_info(stop_id)
    if stop_info is None:
        await update.message.reply_text("Unknown bus stop code")
        return
    busses = get_arriving_busses(stop_id)
    reply_msg = next_bus_msg(stop_info, busses, int(time.time()))

    # refresh button
    reply_markup = InlineKeyboardMarkup(make_refresh_button(stop_id))

    await update.message.reply_text(text=reply_msg, reply_markup=reply_markup)


async def bus_route(
    get_route_stops: GetRouteStops, update: Update, bus_number: str | None
) -> None:
    """
    reply user with bus route information
    """
    if update.message is None:
        return

    if bus_number is None:
        await update.message.reply_text("Please provide a bus number")
        return

    # craft message
    route_info = get_route_stops(bus_number, 1)
    if route_info is None:
        await update.message.reply_text("Unknown bus number")
        return
    reply_msg = bus_route_msg(bus_number, route_info)

    # refresh button
    reply_markup = InlineKeyboardMarkup(make_change_route_btn(bus_number, 2))

    await update.message.reply_text(text=reply_msg, reply_markup=reply_markup)


async def search(
    search_possible_stops: SearchPossibleStops, update: Update, query: list[str]
) -> None:
    if update.message is None:
        return
    possible_stops = search_possible_stops(query)
    reply_msg = bus_stop_search_msg(possible_stops)

    await update.message.reply_text(text=reply_msg)


async def unknown_command(update: Update) -> None:
    """
    reply user to indicate unknown command
    """
    if update.message is None:
        return
    await update.message.reply_text("Unknown command")
