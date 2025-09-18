from typing import Callable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from bus_service.adapter import BusServiceAdapter
from bus_service.bus_stops import GetStopInfo
from constants import SETTINGS_ACTIONS
from storage.adapter import StorageUtility
from utils import get_chat_id


BACK_TO_SETTINGS_BUTTON = [
    InlineKeyboardButton("Back to settings", callback_data=SETTINGS_ACTIONS.SHOW.value)
]


SETTINGS_KEYBOARD = [
    [
        InlineKeyboardButton(
            "Remove stops", callback_data=SETTINGS_ACTIONS.REMOVE_FLOW.value
        )
    ],
    [
        InlineKeyboardButton(
            "Reorder stops", callback_data=SETTINGS_ACTIONS.REORDER_FLOW.value
        )
    ],
    [
        InlineKeyboardButton(
            "Revoke permissions", callback_data=SETTINGS_ACTIONS.DECLINE_FLOW.value
        )
    ],
]


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

        reply_msg = "User configuration settings will not be stored."
        await query.answer()
        try:
            await query.edit_message_text(text=reply_msg)
        except BadRequest:
            # ignore errors due to same message being sent
            pass

    return settings_consent_revoke


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
            return await ask_consent(update, context)

        text = "Choose an option from the list below:"
        reply_markup = InlineKeyboardMarkup(SETTINGS_KEYBOARD)
        if update.message is not None:
            await update.message.reply_text(text=text, reply_markup=reply_markup)
        elif update.callback_query is not None:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text=text, reply_markup=reply_markup
            )

    return show_settings


async def save_stop(
    storage_utility: StorageUtility,
    get_stop_info: GetStopInfo,
    update: Update,
    stop_id: str,
) -> None:
    if update.message is None:
        return

    user_exists = storage_utility.check_user_exists(update.message.chat_id)
    if not user_exists:
        return await settings_not_enabled_message(update)

    stop_info = get_stop_info(stop_id)
    if stop_info is None:
        await update.message.reply_text("Unable to save unknown bus stop code")
        return

    storage_utility.save_stop(update.message.chat_id, stop_id)
    # TODO use message formatter
    await update.message.reply_text(
        f"""Saved bus stop
{stop_info["BusStopCode"]} | {stop_info["Description"]}"""
    )


def __make_saved_stops_list(
    get_stop_info: GetStopInfo,
    saved_stops: list[str],
    settings_action: SETTINGS_ACTIONS,
) -> list[list[InlineKeyboardButton]]:
    """
    TODO describe
    """
    buttons: list[list[InlineKeyboardButton]] = []
    for stop in saved_stops:
        stop_info = get_stop_info(stop)
        if stop_info is not None:
            button = InlineKeyboardButton(
                f"{stop_info['BusStopCode']} | {stop_info['Description']}",
                callback_data=f"{settings_action.value},{stop_info['BusStopCode']}",
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
            return await settings_not_enabled_message(update)

        saved_stops = storage_utility.get_saved_stops(chat_id)
        if len(saved_stops) > 0:
            text = "Remove a stop from the list below:"
        else:
            text = "List is empty."
        callback_buttons = __make_saved_stops_list(
            get_stop_info, saved_stops, SETTINGS_ACTIONS.REMOVE
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
            return await settings_not_enabled_message(update)

        stop_id = query.data.split(",")[1]
        storage_utility.remove_stop(chat_id, stop_id)

        remove_flow = remove_flow_handler(storage_utility, get_stop_info)
        await remove_flow(update, context)

    return remove_stop


def reorder_flow_handler(
    storage_utility: StorageUtility, get_stop_info: GetStopInfo
) -> Callable:
    async def reorder_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        TODO handle scenario where stops exist or don't exist already
        """
        query = update.callback_query
        chat_id = get_chat_id(update, context)
        if query is None or query.data is None or chat_id is None:
            return  # ignore malformed requests

        user_exists = storage_utility.check_user_exists(chat_id)
        if not user_exists:
            return await settings_not_enabled_message(update)

        saved_stops = storage_utility.get_saved_stops(chat_id)
        text = "Select a stop to reorder from the list below:"
        callback_buttons = __make_saved_stops_list(
            get_stop_info, saved_stops, SETTINGS_ACTIONS.REORDER_SELECT
        ) + [BACK_TO_SETTINGS_BUTTON]
        reply_markup = InlineKeyboardMarkup(callback_buttons)
        await query.answer()
        await query.edit_message_text(text=text, reply_markup=reply_markup)

    return reorder_flow


def __make_reorder_keyboard(stop_id: str, position: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Up",
                    callback_data=f"{SETTINGS_ACTIONS.REORDER.value},{stop_id},{position},{0}",
                ),
                InlineKeyboardButton(
                    "Down",
                    callback_data=f"{SETTINGS_ACTIONS.REORDER.value},{stop_id},{position},{1}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "Done", callback_data=SETTINGS_ACTIONS.REORDER_FLOW.value
                ),
            ],
        ]
    )


def __get_reorder_list_message(
    get_stop_info: GetStopInfo, saved_stops: list[str], selected_pos: int
) -> str:
    """
    Displays the order of the current list of saved stops

    Uses 1 based indexing
    """
    msg = ""
    stop_info_iter = map(get_stop_info, saved_stops)
    for idx, stop_info in enumerate(stop_info_iter):
        if stop_info is not None:
            marker = "🔴 " if idx == selected_pos else ""
            msg += f"{marker}{idx + 1}. {stop_info['BusStopCode']} | {stop_info['Description']}\n"
    msg += "\n🔴 Currently selected stop"
    return msg


def reorder_select_handler(
    storage_utility: StorageUtility, get_stop_info: GetStopInfo
) -> Callable:
    async def reorder_select(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        TODO handle scenario where stops exist or don't exist already
        """
        query = update.callback_query
        chat_id = context._chat_id
        if query is None or query.data is None or chat_id is None:
            return  # ignore malformed requests

        user_exists = storage_utility.check_user_exists(chat_id)
        if not user_exists:
            return await settings_not_enabled_message(update)

        selected_stop_id = query.data.split(",")[1]

        saved_stops = storage_utility.get_saved_stops(chat_id)
        try:
            idx = saved_stops.index(selected_stop_id)
            text = __get_reorder_list_message(get_stop_info, saved_stops, idx)
            reply_markup = __make_reorder_keyboard(selected_stop_id, idx)
            await query.answer()
            await query.edit_message_text(text, reply_markup=reply_markup)

        except ValueError:
            text = "Data for this message is outdated. Please use /settings for the latest data."
            await query.answer()
            await query.edit_message_text(text)

        except BadRequest:
            pass  # ignore errors due to same message being sent

    return reorder_select


def __reorder_stops_list(saved_stops: list[str], pos: int, dir: str) -> list[str]:
    ls = saved_stops[::]
    target = saved_stops[pos]
    if dir == "0":  # move forward
        if pos == 0:
            # already first item
            return ls
        ls[pos] = ls[pos - 1]
        ls[pos - 1] = target
    else:  # move backwards
        if pos == len(saved_stops) - 1:
            # already last item
            return ls
        ls[pos] = ls[pos + 1]
        ls[pos + 1] = target
    return ls


def reorder_handler(
    storage_utility: StorageUtility, get_stop_info: GetStopInfo
) -> Callable:
    async def reorder_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            return await settings_not_enabled_message(update)

        _, stop_id, position, direction = query.data.split(",")
        saved_stops = storage_utility.get_saved_stops(chat_id)
        # validate the stop exists at that position
        if saved_stops[int(position)] != stop_id:
            # TODO show error about invalid data
            return
        new_stops_order = __reorder_stops_list(saved_stops, int(position), direction)
        storage_utility.save_stops(chat_id, new_stops_order)

        reorder_select = reorder_select_handler(storage_utility, get_stop_info)
        await reorder_select(update, context)

    return reorder_stop


def register_settings_handlers(
    application: Application,
    bus_service_adapter: BusServiceAdapter,
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
            pattern=SETTINGS_ACTIONS.DECLINE_FLOW.value,
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
            remove_flow_handler(storage_utility, bus_service_adapter.get_stop_info),
            pattern=SETTINGS_ACTIONS.REMOVE_FLOW.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            remove_handler(storage_utility, bus_service_adapter.get_stop_info),
            pattern=rf"{SETTINGS_ACTIONS.REMOVE.value},\d{{5}}",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            reorder_flow_handler(storage_utility, bus_service_adapter.get_stop_info),
            pattern=SETTINGS_ACTIONS.REORDER_FLOW.value,
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            reorder_select_handler(storage_utility, bus_service_adapter.get_stop_info),
            pattern=rf"{SETTINGS_ACTIONS.REORDER_SELECT.value},\d{{5}}",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            reorder_handler(storage_utility, bus_service_adapter.get_stop_info),
            pattern=rf"{SETTINGS_ACTIONS.REORDER.value},\d{{5}},\d,[01]",
        )
    )
