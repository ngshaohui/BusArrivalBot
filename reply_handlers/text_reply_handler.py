import re

from telegram import Message, Update
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from bus_service.bus_stops import SearchPossibleStops
from message_formatters.bus_stop_search import bus_stop_search_msg
from reply_handlers.saved_stops import list_saved_stops
from reply_handlers.settings_handler import save_stop

from .bus_arrival import REGEX_STOP_CODE, bus_stop_handler
from .bus_route import REGEX_ROUTE, route_direction_handler
from .saved_stops import REGEX_LIST_SAVED_STOPS
from .settings_handler import REGEX_ADD_STOP

# search opp heavy
# /search pei
REGEX_SEARCH = r"\/?search\s*(.*)"


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

    if re.match(REGEX_STOP_CODE, msg_text):
        await bus_stop_handler(update, context)
    elif re.match(REGEX_ROUTE, msg_text, re.IGNORECASE):
        # TODO: caveat - does not handle /route (without a number)
        await route_direction_handler(update, context)
    elif m := re.match(REGEX_SEARCH, msg_text, re.IGNORECASE):
        query_str = m.group(1)
        query: list[str] = re.split(r"[\s\/\-]", query_str)
        await search(app_state.bus_service.search_possible_stops, message, query)
    elif re.match(REGEX_ADD_STOP, msg_text, re.IGNORECASE):
        await save_stop(update, context)
    elif re.match(REGEX_LIST_SAVED_STOPS, msg_text, re.IGNORECASE) is not None:
        await list_saved_stops(update, context)
    else:
        # unknown command message
        await unknown_command(message)


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
