from enum import IntEnum, auto

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from utils.bot_utils import get_chat_id
from utils.constants import SETTINGS_ACTIONS, SYMBOLS_LEGEND
from utils.custom_typings import UserSettings

from .inline_buttons import BACK_TO_SETTINGS_BUTTON


class SymbolOptions(IntEnum):
    SHOW_LOAD = auto()
    SHOW_TYPE = auto()


async def show_symbols_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Allow user to configure showing bus load and bus type
    """
    query = update.callback_query

    chat_id = get_chat_id(update, context)
    if chat_id is None or query is None or query.data is None:
        return  # ignore malformed request

    app_state = get_app_state(context.application)
    user_settings = await app_state.user_data_adapter.get_user_settings(chat_id)

    # change config in settings
    parts = query.data.split(",")
    if len(parts) == 3:
        option = int(parts[1])
        value = bool(int(parts[2]))
        match option:
            case SymbolOptions.SHOW_LOAD.value:
                await app_state.user_data_adapter.save_user_settings(
                    chat_id, value, user_settings.show_type
                )
                # preemptively use given value to display
                user_settings = UserSettings(value, user_settings.show_type)
            case SymbolOptions.SHOW_TYPE.value:
                await app_state.user_data_adapter.save_user_settings(
                    chat_id, user_settings.show_load, value
                )
                user_settings = UserSettings(user_settings.show_load, value)

    text = f"""Show symbols for bus arrival information
Bus **Load** (**{"enabled ✅" if user_settings.show_load else "disabled"}**)
Bus Type (**{"enabled ✅" if user_settings.show_type else "disabled"}**)

{SYMBOLS_LEGEND}"""

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"{'Enable' if not user_settings.show_load else 'Disable'} Bus Load",
                    callback_data=f"{SETTINGS_ACTIONS.SYMBOL_SHOW.value},{SymbolOptions.SHOW_LOAD.value},{int(not user_settings.show_load)}",
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'Enable' if not user_settings.show_type else 'Disable'} Bus Type",
                    callback_data=f"{SETTINGS_ACTIONS.SYMBOL_SHOW.value},{SymbolOptions.SHOW_TYPE.value},{int(not user_settings.show_type)}",
                )
            ],
            BACK_TO_SETTINGS_BUTTON,
        ]
    )

    try:
        await query.answer()
        await query.edit_message_text(
            text=text, reply_markup=reply_markup, parse_mode="Markdown"
        )
    except BadRequest:
        pass  # ignore errors due to same message being sent from repeated button spamming
