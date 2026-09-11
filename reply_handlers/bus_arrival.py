import asyncio
import re
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from bus_service.bus_arrival import get_arriving_busses
from message_formatters.bus_arrival import next_bus_msg
from utils.bot_utils import get_chat_id

# 34120
# /29125
REGEX_STOP_CODE = r"\/?(\d{5})"


def make_refresh_button(stop_id: str) -> list[list[InlineKeyboardButton]]:
    "button to refresh arrival timings"
    return [[InlineKeyboardButton("Refresh", callback_data=stop_id)]]


async def bus_stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    handles both message replies and callback query handlers
    """
    message = update.message
    query = update.callback_query
    chat_id = get_chat_id(update, None)

    if chat_id is None:
        # TODO: log when this occurs
        return  # ignore malformed message

    has_message = message is not None and message.text is not None
    has_query = query is not None and query.data is not None

    stop_id_candidate = ""
    if has_message:
        stop_id_candidate = message.text
    elif has_query:
        stop_id_candidate = query.data
    m = re.match(REGEX_STOP_CODE, stop_id_candidate)
    if m is None:
        return  # unreachable, pacifying type checker
    stop_id = m.group(1)

    # craft message
    reply_msg = ""
    app_state = get_app_state(context.application)
    stop_info = app_state.bus_service.get_stop_info(stop_id)
    if stop_info is None:
        reply_msg = "Unknown bus stop code"
    (busses, user_settings) = await asyncio.gather(
        get_arriving_busses(stop_id),
        app_state.user_data_adapter.get_user_settings(chat_id),
    )
    if busses is None:
        reply_msg = (
            "Currently experiencing issues with LTA's API, please try again later"
        )
    if stop_info is not None and busses is not None:
        reply_msg = next_bus_msg(stop_info, busses, int(time.time()), user_settings)

    reply_markup = InlineKeyboardMarkup(make_refresh_button(stop_id))

    if has_message:
        await message.reply_text(text=reply_msg, reply_markup=reply_markup)
    elif has_query:
        await query.answer()
        try:
            await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
        except BadRequest:
            # Query is too old and response timeout expired or query id is invalid
            pass  # ignore errors due to same message being sent
