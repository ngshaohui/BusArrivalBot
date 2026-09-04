import re
import time

from telegram import InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from bus_service.adapter import GetRouteStops
from bus_service.bus_arrival import get_arriving_busses
from bus_service.bus_stops import GetStopInfo, SearchPossibleStops
from message_formatters.bus_arrival import next_bus_msg
from message_formatters.bus_route import bus_route_msg
from message_formatters.bus_stop_search import bus_stop_search_msg
from reply_handlers.settings_handler import save_stop
from user_data.saved_stops import list_saved_stops

from .inline_buttons import make_change_route_btn, make_refresh_button

# 34120
# /29125
REGEX_STOP_CODE = r"\/?(\d{5})"
# 67
# /961M
REGEX_BUS_NUM = r"^\/?(\d{1,3}[A-Za-z]?)$"
# route 2
# /route 307E
REGEX_ROUTE = r"\/?route\s*(\d{1,3}[A-Za-z]?)?"
# search opp heavy
# /search pei
REGEX_SEARCH = r"\/?search\s*(.*)"
# add 42071
# /add 43099
# add_01019
# /add_59159
REGEX_ADD_STOP = r"\/?add[?:\s*|_](\d{5})"
# list
# /list
REGEX_LIST_SAVED_STOPS = r"\/?list"


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    parse all text that the user sends

    this function then sends the request to the specific handler
    """
    message = update.message
    if message is None or message.text is None:
        return
    msg_text = message.text
    app_state = get_app_state(context.application)

    if m := re.match(REGEX_STOP_CODE, msg_text):
        stop_code = m.group(1)
        await bus_stop_code(app_state.bus_service.get_stop_info, message, stop_code)
    elif m := re.match(REGEX_BUS_NUM, msg_text, re.IGNORECASE):
        bus_number = m.group(1)
        await bus_route(app_state.bus_service.get_route_stops, message, bus_number)
    elif m := re.match(REGEX_ROUTE, msg_text, re.IGNORECASE):
        # TODO consider deprecating this command
        bus_number = m.group(1)
        await bus_route(app_state.bus_service.get_route_stops, message, bus_number)
    elif m := re.match(REGEX_SEARCH, msg_text, re.IGNORECASE):
        query_str = m.group(1)
        query: list[str] = re.split(r"[\s\/\-]", query_str)
        await search(app_state.bus_service.search_possible_stops, message, query)
    elif m := re.match(REGEX_ADD_STOP, msg_text, re.IGNORECASE):
        stop_code = m.group(1)
        await save_stop(
            app_state.storage_utility,
            app_state.bus_service.get_stop_info,
            update,
            stop_code,
        )
    elif re.match(REGEX_LIST_SAVED_STOPS, msg_text, re.IGNORECASE) is not None:
        await list_saved_stops(
            app_state.storage_utility, app_state.bus_service.get_stop_info, update
        )
    else:
        # unknown command message
        await unknown_command(message)


async def bus_stop_code(
    get_stop_info: GetStopInfo, message: Message, stop_id: str
) -> None:
    """
    reply user with bus arrival information
    """
    # craft message
    stop_info = get_stop_info(stop_id)
    if stop_info is None:
        await message.reply_text("Unknown bus stop code")
        return
    busses = get_arriving_busses(stop_id)
    if busses is None:
        await message.reply_text(
            "Currently experiencing issues with LTA's API, please try again later"
        )
        return
    reply_msg = next_bus_msg(stop_info, busses, int(time.time()))

    # refresh button
    reply_markup = InlineKeyboardMarkup(make_refresh_button(stop_id))

    await message.reply_text(text=reply_msg, reply_markup=reply_markup)


async def bus_route(
    get_route_stops: GetRouteStops, message: Message, bus_number: str | None
) -> None:
    """
    reply user with bus route information
    """
    if bus_number is None:
        await message.reply_text("Please provide a bus number")
        return

    # craft message
    bus_number = bus_number.upper()
    route_info = get_route_stops(bus_number, 1)
    if route_info is None:
        await message.reply_text("Unknown bus number")
        return
    reply_msg = bus_route_msg(bus_number, route_info)

    # refresh button
    reply_markup = InlineKeyboardMarkup(make_change_route_btn(bus_number, 2))

    await message.reply_text(text=reply_msg, reply_markup=reply_markup)


async def search(
    search_possible_stops: SearchPossibleStops, message: Message, query: list[str]
) -> None:
    possible_stops = search_possible_stops(query)
    reply_msg = bus_stop_search_msg(possible_stops)

    await message.reply_text(text=reply_msg)


async def unknown_command(message: Message) -> None:
    """
    reply user to indicate unknown command
    """
    await message.reply_text("Unknown command")
