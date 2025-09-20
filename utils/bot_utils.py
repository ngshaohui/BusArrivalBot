from telegram import Update
from telegram.ext import ContextTypes


def get_chat_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE | None
) -> int | None:
    """
    get chat id from message/update context
    """
    if update.message is not None:
        return update.message.chat_id
    elif context is not None and context._chat_id is not None:
        return context._chat_id
    return None
