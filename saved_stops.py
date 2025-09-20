from telegram import InlineKeyboardMarkup, Update

from bus_service.bus_stops import GetStopInfo
from reply_handlers.inline_buttons import get_stop_inline_button
from reply_handlers.settings_handler import settings_not_enabled_message
from storage.adapter import StorageUtility
from utils.custom_typings import BusStop
from utils.bot_utils import get_chat_id


async def list_saved_stops(
    storage_utility: StorageUtility,
    get_stop_info: GetStopInfo,
    update: Update,
) -> None:
    """
    displays the list of saved stops
    TODO: indicate when a saved stop is no longer present
    """
    chat_id = get_chat_id(update, None)
    if not chat_id or update.message is None:
        return  # ignore malformed requests

    user_exists = storage_utility.check_user_exists(update.message.chat_id)
    if not user_exists:
        return await settings_not_enabled_message(update)

    saved_stops = storage_utility.get_saved_stops(chat_id)
    stops_iterable = map(get_stop_info, saved_stops)
    stops: list[BusStop] = []
    # TODO: indicate when a saved stop is no longer present
    for stop in stops_iterable:
        if stop is not None:
            stops.append(stop)

    # build keyboard
    text = "Pick a list of saved stops from the list below"
    keyboard = list(map(get_stop_inline_button, stops))
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
