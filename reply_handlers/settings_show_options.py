from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .inline_buttons import SETTINGS_KEYBOARD


async def show_settings_options(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Choose an option from the list below:"
    reply_markup = InlineKeyboardMarkup(SETTINGS_KEYBOARD)
    if update.message is not None:
        await update.message.reply_text(text=text, reply_markup=reply_markup)
    elif update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text, reply_markup=reply_markup
        )
