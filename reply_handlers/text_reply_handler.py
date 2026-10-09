import re

from telegram import Update
from telegram.ext import ContextTypes

from .bus_arrival import REGEX_STOP_CODE, bus_stop_handler
from .bus_route import REGEX_ROUTE, REGEX_ROUTE_DANGLING, route_direction_handler
from .bus_stop_search import REGEX_SEARCH, handle_search
from .saved_stops import (
    REGEX_ADD_STOP,
    REGEX_LIST_SAVED_STOPS,
    list_saved_stops,
    save_stop,
)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    parse all text that the user sends

    this function then sends the request to the specific handler
    """
    message = update.message
    if message is None or message.text is None:
        return
    msg_text = message.text

    if re.match(REGEX_STOP_CODE, msg_text):
        await bus_stop_handler(update, context)
    elif re.match(REGEX_ROUTE_DANGLING, msg_text, re.IGNORECASE) or re.match(
        REGEX_ROUTE, msg_text, re.IGNORECASE
    ):
        await route_direction_handler(update, context)
    elif re.match(REGEX_SEARCH, msg_text, re.IGNORECASE):
        await handle_search(update, context)
    elif re.match(REGEX_ADD_STOP, msg_text, re.IGNORECASE):
        await save_stop(update, context)
    elif re.match(REGEX_LIST_SAVED_STOPS, msg_text, re.IGNORECASE) is not None:
        await list_saved_stops(update, context)
    else:
        await message.reply_text("Unknown command")
