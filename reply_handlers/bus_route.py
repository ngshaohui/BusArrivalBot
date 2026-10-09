import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from message_formatters.bus_route import bus_route_msg
from utils.bot_utils import get_chat_id

# route
# /route
REGEX_ROUTE_DANGLING = r"^\/?route$"  # dangling keywords without the bus number
# 67
# /961M
# route 2
# /route 307E
REGEX_ROUTE = r"^\/?(?:route)?\s*(\d{1,3}[A-Za-z]?)$"

_USER_ERR_MSG_DANGLING_ROUTE_COMMAND = """A valid bus number is required for displaying bus route

E.g. `route 67`
"""


async def route_direction_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    gives the route for the other direction
    """
    message = update.message
    query = update.callback_query
    chat_id = get_chat_id(update, None)

    if chat_id is None:
        # TODO: log when this occurs
        return  # ignore malformed message

    has_message = message is not None and message.text is not None
    has_query = query is not None and query.data is not None

    # check for dangling route command
    if has_message:
        m = re.match(REGEX_ROUTE_DANGLING, message.text)
        if m is not None:
            await message.reply_text(
                text=_USER_ERR_MSG_DANGLING_ROUTE_COMMAND, parse_mode="Markdown"
            )

    # obtain bus number and direction
    # TODO: can optimize this since has_query will always return valid bus_number
    bus_number_candidate = ""
    direction = 1
    if has_message:
        bus_number_candidate = message.text
    elif has_query:
        bus_number_candidate, direction_str = query.data.split(",")
        direction = 1 if direction_str == "2" else 2
    m = re.match(REGEX_ROUTE, bus_number_candidate)
    if m is None or m.group(1) is None:  # pacify typechecker
        return
    bus_number = m.group(1)

    # craft message
    app_state = get_app_state(context.application)
    route_info = app_state.bus_service.get_route_stops(bus_number, direction)

    reply_markup: InlineKeyboardMarkup | None = None
    if route_info is None:
        reply_msg = "Unknown bus number"
    else:
        reply_msg = bus_route_msg(bus_number, route_info)
        # refresh button
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Change direction", callback_data=f"{bus_number},{direction}"
                    )
                ]
            ]
        )

    if has_message:
        await message.reply_text(text=reply_msg, reply_markup=reply_markup)
    elif has_query:
        await query.answer()
        try:
            await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
        except BadRequest:
            pass  # ignore errors due to same message being sent
