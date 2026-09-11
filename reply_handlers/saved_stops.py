from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from reply_handlers.inline_buttons import get_stop_inline_button
from reply_handlers.settings_handler import settings_not_enabled_message
from utils.bot_utils import get_chat_id
from utils.custom_typings import BusStop

# list
# /list
REGEX_LIST_SAVED_STOPS = r"\/?list"


async def list_saved_stops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    displays the list of saved stops
    TODO: indicate when a saved stop is no longer present
    """
    chat_id = get_chat_id(update, None)
    if not chat_id or update.message is None:
        return  # ignore malformed requests

    app_state = get_app_state(context.application)
    user_exists = await app_state.user_data_adapter.check_user_exists(chat_id)
    if not user_exists:
        return await settings_not_enabled_message(update)

    saved_stops = await app_state.user_data_adapter.get_saved_stops(chat_id)
    stops: list[BusStop] = [
        stop
        for stop in map(app_state.bus_service.get_stop_info, saved_stops)
        if stop is not None
    ]
    # TODO: indicate when a saved stop is no longer present

    # build keyboard
    if len(stops) == 0:
        text = """List is currently empty.

You can add any BusStopCode to this list for quick access
`add 08031`"""
        reply_markup = None
    else:
        text = "Pick a list of saved stops from the list below"
        reply_markup = InlineKeyboardMarkup(
            [get_stop_inline_button(stop) for stop in stops]
        )

    await update.message.reply_text(
        text=text, parse_mode="Markdown", reply_markup=reply_markup
    )
