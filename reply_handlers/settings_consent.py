from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from utils.bot_utils import get_chat_id
from utils.constants import SETTINGS_ACTIONS

from .settings_show_options import show_settings_options

SETTINGS_CONSENT_KEYBOARD = [
    [
        InlineKeyboardButton("Allow", callback_data=SETTINGS_ACTIONS.CONSENT.value),
        InlineKeyboardButton("Decline", callback_data=SETTINGS_ACTIONS.DECLINE.value),
    ]
]


SETTINGS_REVOKE_CONSENT_KEYBOARD = [
    [
        InlineKeyboardButton("Confirm", callback_data=SETTINGS_ACTIONS.DECLINE.value),
        InlineKeyboardButton("Cancel", callback_data=SETTINGS_ACTIONS.SHOW.value),
    ]
]


async def settings_consent_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    handle user granting consent
    """
    chat_id = get_chat_id(update, context)
    if not chat_id:
        return  # ignore malformed requests

    app_state = get_app_state(context.application)
    await app_state.user_data_adapter.add_user(chat_id)
    await show_settings_options(update, context)


async def revoke_consent_confirmation_handler(
    update: Update, _: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    if query is None or query.data is None:
        return  # ignore malformed requests

    # confirm revocation of consent
    reply_msg = """Are you sure you want to revoke data storage consent?
This will delete your saved stops.

This action is irreversible."""
    reply_markup = InlineKeyboardMarkup(SETTINGS_REVOKE_CONSENT_KEYBOARD)

    await query.answer()
    try:
        await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
    except BadRequest:
        # ignore errors due to same message being sent
        pass


async def revoke_consent_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    handle user removing settings consent
    """
    query = update.callback_query
    chat_id = context._chat_id
    if query is None or query.data is None or chat_id is None:
        return

    app_state = get_app_state(context.application)
    await app_state.user_data_adapter.remove_user(chat_id)

    reply_msg = "User configuration settings will not be stored."
    await query.answer()
    try:
        await query.edit_message_text(text=reply_msg)
    except BadRequest:
        # ignore errors due to same message being sent
        pass


async def settings_not_enabled_message(update: Update) -> None:
    """
    Show message to user indicating that they need to visit /settings to consent first
    """
    text = "User configuration settings not found. Visit /settings to enable storage first."
    if update.message is not None:
        await update.message.reply_text(text=text)
    elif update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text)


async def ask_consent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    ask user for consent to save settings
    """
    text = """No existing user configuration settings found.

Allow the bot to store your settings data?"""
    reply_markup = InlineKeyboardMarkup(SETTINGS_CONSENT_KEYBOARD)
    if update.message is not None:
        await update.message.reply_text(text=text, reply_markup=reply_markup)
    elif update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text, reply_markup=reply_markup
        )
