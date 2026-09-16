from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from bot_app_state import get_app_state
from utils.bot_utils import get_chat_id
from utils.constants import SETTINGS_ACTIONS

from .saved_stops import (
    remove_flow_handler,
    remove_stop_handler,
    reorder_flow_handler,
    reorder_select_handler,
    reorder_stop_handler,
)
from .settings_consent import (
    ask_consent,
    revoke_consent_confirmation_handler,
    revoke_consent_handler,
    settings_consent_handler,
)
from .settings_show_options import show_settings_options
from .settings_symbols import show_symbols_handler


async def show_settings_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = get_chat_id(update, context)
    if chat_id is None:
        return  # ignore malformed requests

    app_state = get_app_state(context.application)
    user_exists = await app_state.user_data_adapter.check_user_exists(chat_id)
    if not user_exists:
        return await ask_consent(update, context)
    await show_settings_options(update, context)


def register_settings_handlers(
    application: Application,
) -> None:
    """
    register settings handlers
    """
    application.add_handler(
        CallbackQueryHandler(
            show_settings_handler,
            pattern=SETTINGS_ACTIONS.SHOW.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            settings_consent_handler,
            pattern=SETTINGS_ACTIONS.CONSENT.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            revoke_consent_confirmation_handler,
            pattern=SETTINGS_ACTIONS.DECLINE_FLOW.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            revoke_consent_handler,
            pattern=SETTINGS_ACTIONS.DECLINE.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            remove_flow_handler,
            pattern=SETTINGS_ACTIONS.REMOVE_FLOW.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            remove_stop_handler,
            pattern=rf"{SETTINGS_ACTIONS.REMOVE.value},\d{{5}}",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            reorder_flow_handler,
            pattern=SETTINGS_ACTIONS.REORDER_FLOW.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            reorder_select_handler,
            pattern=rf"{SETTINGS_ACTIONS.REORDER_SELECT.value},\d{{5}}",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            reorder_stop_handler,
            pattern=rf"{SETTINGS_ACTIONS.REORDER.value},\d{{5}},\d,[01]",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            show_symbols_handler,
            pattern=rf"{SETTINGS_ACTIONS.SYMBOL_SHOW.value}(,\d,[01])?",
        )
    )
