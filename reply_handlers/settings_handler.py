from typing import Callable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from bus_stops import GetStopInfo
from constants import SETTINGS_ACTIONS
from service_integrator import ServiceIntegrator
from storage.adapter import StorageUtility


def __make_settings_buttons() -> list[list[InlineKeyboardButton]]:
    """ """
    remove_button = InlineKeyboardButton(
        "Remove stops", callback_data=SETTINGS_ACTIONS.REMOVE_FLOW.value
    )
    # reorder_button = InlineKeyboardButton(
    #     "Reorder", callback_data=SETTINGS_ACTIONS.REORDER.value
    # )
    return [[remove_button]]


SETTINGS_BUTTONS = __make_settings_buttons()


def __make_settings_consent_buttons() -> list[list[InlineKeyboardButton]]:
    """
    buttons to ask for consent to store data
    """
    consent_button = InlineKeyboardButton(
        "Consent", callback_data=SETTINGS_ACTIONS.CONSENT.value
    )
    decline_button = InlineKeyboardButton(
        "Decline", callback_data=SETTINGS_ACTIONS.DECLINE.value
    )
    return [[consent_button, decline_button]]


SETTINGS_CONSENT_BUTTONS = __make_settings_consent_buttons()


BACK_TO_SETTINGS_BUTTON = [
    InlineKeyboardButton("Back to settings", callback_data=SETTINGS_ACTIONS.SHOW.value)
]


def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """
    get chat id from message/update context
    TODO: move to a utility file
    """
    if update.message is not None:
        return update.message.chat_id
    elif context._chat_id is not None:
        return context._chat_id
    return None


def settings_consent_handler(storage_utility: StorageUtility) -> Callable:
    """
    handle settings consent
    """

    async def settings_consent(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        chat_id = get_chat_id(update, context)
        if not chat_id:
            return  # ignore malformed requests
        storage_utility.save_stops(chat_id, [])
        settings_handler = show_settings_handler(storage_utility)
        await settings_handler(update, context)

    return settings_consent


def revoke_consent_confirmation_handler() -> Callable:
    """
    handle confirmation to revoke settings consent
    """

    async def settings_consent_revoke_confirmation(
        update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        if query is None or query.data is None:
            return  # ignore malformed requests

        # confirm revocation of consent
        reply_msg = """Are you sure you want to revoke consent?
This will delete your saved stops.

This action is irreversible."""
        reply_markup = InlineKeyboardMarkup(SETTINGS_CONSENT_BUTTONS)

        await query.answer()
        try:
            await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
        except BadRequest:
            # ignore errors due to same message being sent
            pass

    return settings_consent_revoke_confirmation


def revoke_consent_handler(storage_utility: StorageUtility) -> Callable:
    """
    handle removing settings consent
    """

    async def settings_consent_revoke(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        chat_id = context._chat_id
        if query is None or query.data is None or chat_id is None:
            return
        storage_utility.remove_user(chat_id)

        reply_msg = "Consent revoked."
        await query.answer()
        try:
            await query.edit_message_text(text=reply_msg)
        except BadRequest:
            # ignore errors due to same message being sent
            pass

    return settings_consent_revoke


async def __show_info(update: Update) -> None:
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
    text = "Allow the bot to store your settings?"
    reply_markup = InlineKeyboardMarkup(SETTINGS_CONSENT_BUTTONS)
    if update.message is not None:
        await update.message.reply_text(text=text, reply_markup=reply_markup)
    elif update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text, reply_markup=reply_markup
        )
    return


def show_settings_handler(storage_utility: StorageUtility) -> Callable:
    async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        TODO handle scenario where stops exist or don't exist already
        TODO have the user agree to store settings first, can check if exists in db
        TODO revoke consent
        """
        chat_id = get_chat_id(update, context)
        if chat_id is None:
            return  # ignore malformed requests
        user_exists = storage_utility.check_user_exists(chat_id)
        if not user_exists:
            return await ask_consent(update, context)  # TODO

        text = "Choose an option:"
        reply_markup = InlineKeyboardMarkup(SETTINGS_BUTTONS)
        if update.message is not None:
            await update.message.reply_text(text=text, reply_markup=reply_markup)
        elif update.callback_query is not None:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text=text, reply_markup=reply_markup
            )

    return show_settings


async def add_stop(
    storage_utility: StorageUtility,
    get_stop_info: GetStopInfo,
    update: Update,
    stop_id: str,
) -> None:
    if update.message is None:
        return

    user_exists = storage_utility.check_user_exists(update.message.chat_id)
    if not user_exists:
        return await __show_info(update)

    stop_info = get_stop_info(stop_id)
    if stop_info is None:
        await update.message.reply_text("Unknown bus stop code")
        return

    storage_utility.add_stop(update.message.chat_id, stop_id)
    # TODO use message formatter
    await update.message.reply_text(
        f"Added bus stop {stop_info['BusStopCode']} {stop_info['Description']}"
    )


def __make_saved_stops_removal_list(
    get_stop_info: GetStopInfo, saved_stops: list[str]
) -> list[list[InlineKeyboardButton]]:
    """
    TODO describe
    """
    buttons = []
    for stop in saved_stops:
        stop_info = get_stop_info(stop)
        if stop_info is not None:
            button = InlineKeyboardButton(
                f"{stop_info['BusStopCode']} {stop_info['Description']}",
                callback_data=f"{SETTINGS_ACTIONS.REMOVE.value},{stop_info['BusStopCode']}",
            )
            buttons.append([button])
    return buttons


def remove_flow_handler(
    storage_utility: StorageUtility, get_stop_info: GetStopInfo
) -> Callable:
    async def remove_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        TODO handle scenario where stops exist or don't exist already
        """
        query = update.callback_query
        chat_id = get_chat_id(update, context)
        if query is None or query.data is None or chat_id is None:
            # ignore malformed requests
            return

        user_exists = storage_utility.check_user_exists(chat_id)
        if not user_exists:
            return await __show_info(update)

        saved_stops = storage_utility.get_saved_stops(chat_id)
        if len(saved_stops) > 0:
            text = "Remove a stop from the list below:"
        else:
            text = "List is empty."
        callback_buttons = __make_saved_stops_removal_list(
            get_stop_info, saved_stops
        ) + [BACK_TO_SETTINGS_BUTTON]
        reply_markup = InlineKeyboardMarkup(callback_buttons)
        await query.answer()
        await query.edit_message_text(text=text, reply_markup=reply_markup)

    return remove_flow


def remove_handler(
    storage_utility: StorageUtility, get_stop_info: GetStopInfo
) -> Callable:
    async def remove_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        TODO handle scenario where stops exist or don't exist already
        """
        query = update.callback_query
        chat_id = context._chat_id
        if query is None or query.data is None or chat_id is None:
            # ignore malformed requests
            return

        user_exists = storage_utility.check_user_exists(chat_id)
        if not user_exists:
            return await __show_info(update)

        stop_id = query.data.split(",")[1]
        storage_utility.remove_stop(chat_id, stop_id)

        remove_flow = remove_flow_handler(storage_utility, get_stop_info)
        await remove_flow(update, context)

    return remove_stop


def register_settings_handlers(
    application: Application,
    service_integrator: ServiceIntegrator,
    storage_utility: StorageUtility,
) -> None:
    """
    register settings handlers
    """
    application.add_handler(
        CallbackQueryHandler(
            show_settings_handler(storage_utility),
            pattern=SETTINGS_ACTIONS.SHOW.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            settings_consent_handler(storage_utility),
            pattern=SETTINGS_ACTIONS.CONSENT.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            revoke_consent_confirmation_handler(),
            pattern=SETTINGS_ACTIONS.DECLINE_CONFIRM.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            revoke_consent_handler(storage_utility),
            pattern=SETTINGS_ACTIONS.DECLINE.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            remove_flow_handler(storage_utility, service_integrator.get_stop_info),
            pattern=SETTINGS_ACTIONS.REMOVE_FLOW.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            remove_handler(storage_utility, service_integrator.get_stop_info),
            pattern=rf"{SETTINGS_ACTIONS.REMOVE.value},\d{{5}}",
        )
    )
