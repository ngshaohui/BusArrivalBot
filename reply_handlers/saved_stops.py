import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from bus_service.bus_stops import GetStopInfo
from utils.bot_utils import get_chat_id
from utils.constants import SETTINGS_ACTIONS
from utils.custom_typings import BusStop

from .inline_buttons import BACK_TO_SETTINGS_BUTTON, get_stop_inline_button
from .settings_consent import settings_not_enabled_message

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


# add 42071
# /add 43099
# add_01019
# /add_59159
REGEX_ADD_STOP = r"\/?add[?:\s*|_](\d{5})"


async def save_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return

    app_state = get_app_state(context.application)
    user_exists = await app_state.user_data_adapter.check_user_exists(
        update.message.chat_id
    )
    if not user_exists:
        return await settings_not_enabled_message(update)

    m = re.match(REGEX_ADD_STOP, update.message.text)
    if m is None:
        return  # unreachable, pacifying type checker
    stop_id = m.group(1)

    stop_info = app_state.bus_service.get_stop_info(stop_id)
    if stop_info is None:
        await update.message.reply_text("Unable to save unknown bus stop code")
        return

    await app_state.user_data_adapter.add_stop(update.message.chat_id, stop_id)
    # TODO use message formatter
    await update.message.reply_text(
        f"""Saved bus stop
{stop_info["BusStopCode"]} | {stop_info["Description"]}"""
    )


def _make_saved_stops_list(
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


async def remove_flow_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    TODO handle scenario where stops exist or don't exist already
    """
    query = update.callback_query
    chat_id = get_chat_id(update, context)
    if query is None or query.data is None or chat_id is None:
        # ignore malformed requests
        return

    app_state = get_app_state(context.application)
    user_exists = await app_state.user_data_adapter.check_user_exists(chat_id)
    if not user_exists:
        return await settings_not_enabled_message(update)

    saved_stops = await app_state.user_data_adapter.get_saved_stops(chat_id)
    if len(saved_stops) > 0:
        text = "Remove a stop from the list below:"
    else:
        text = "List is empty."
    callback_buttons = _make_saved_stops_list(
        app_state.bus_service.get_stop_info,
        saved_stops,
        SETTINGS_ACTIONS.REMOVE,
    ) + [BACK_TO_SETTINGS_BUTTON]
    reply_markup = InlineKeyboardMarkup(callback_buttons)
    await query.answer()
    await query.edit_message_text(text=text, reply_markup=reply_markup)


async def remove_stop_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    TODO handle scenario where stops exist or don't exist already
    """
    query = update.callback_query
    chat_id = context._chat_id
    if query is None or query.data is None or chat_id is None:
        # ignore malformed requests
        return

    app_state = get_app_state(context.application)
    user_exists = await app_state.user_data_adapter.check_user_exists(chat_id)
    if not user_exists:
        return await settings_not_enabled_message(update)

    stop_id = query.data.split(",")[1]
    await app_state.user_data_adapter.remove_stop(chat_id, stop_id)

    await remove_flow_handler(update, context)


async def reorder_flow_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    TODO handle scenario where stops exist or don't exist already
    """
    query = update.callback_query
    chat_id = get_chat_id(update, context)
    if query is None or query.data is None or chat_id is None:
        return  # ignore malformed requests

    app_state = get_app_state(context.application)
    user_exists = await app_state.user_data_adapter.check_user_exists(chat_id)
    if not user_exists:
        return await settings_not_enabled_message(update)

    saved_stops = await app_state.user_data_adapter.get_saved_stops(chat_id)
    text = "Select a stop to reorder from the list below:"
    callback_buttons = _make_saved_stops_list(
        app_state.bus_service.get_stop_info,
        saved_stops,
        SETTINGS_ACTIONS.REORDER_SELECT,
    ) + [BACK_TO_SETTINGS_BUTTON]
    reply_markup = InlineKeyboardMarkup(callback_buttons)
    await query.answer()
    await query.edit_message_text(text=text, reply_markup=reply_markup)


def _make_reorder_keyboard(stop_id: str, position: int) -> InlineKeyboardMarkup:
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


def _get_reorder_list_message(
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
            marker = "➡️ " if idx == selected_pos else ""
            msg += f"{marker}{idx + 1}. {stop_info['BusStopCode']} | {stop_info['Description']}\n"
    msg += "\n➡️ Currently selected stop"
    return msg


async def reorder_select_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    TODO handle scenario where stops exist or don't exist already
    """
    query = update.callback_query
    chat_id = context._chat_id
    if query is None or query.data is None or chat_id is None:
        return  # ignore malformed requests

    app_state = get_app_state(context.application)
    user_exists = await app_state.user_data_adapter.check_user_exists(chat_id)
    if not user_exists:
        return await settings_not_enabled_message(update)

    selected_stop_id = query.data.split(",")[1]

    saved_stops = await app_state.user_data_adapter.get_saved_stops(chat_id)
    try:
        idx = saved_stops.index(selected_stop_id)
        text = _get_reorder_list_message(
            app_state.bus_service.get_stop_info, saved_stops, idx
        )
        reply_markup = _make_reorder_keyboard(selected_stop_id, idx)
        await query.answer()
        await query.edit_message_text(text, reply_markup=reply_markup)

    except ValueError:
        text = "Data for this message is outdated. Please use /settings for the latest data."
        await query.answer()
        await query.edit_message_text(text)

    except BadRequest:
        pass  # ignore errors due to same message being sent


def _reorder_stops_list(saved_stops: list[str], pos: int, dir: str) -> list[str]:
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


async def reorder_stop_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    TODO handle scenario where stops exist or don't exist already
    """
    query = update.callback_query
    chat_id = context._chat_id
    if query is None or query.data is None or chat_id is None:
        # ignore malformed requests
        return

    app_state = get_app_state(context.application)
    user_exists = await app_state.user_data_adapter.check_user_exists(chat_id)
    if not user_exists:
        return await settings_not_enabled_message(update)

    _, stop_id, position, direction = query.data.split(",")
    saved_stops = await app_state.user_data_adapter.get_saved_stops(chat_id)
    # validate the stop exists at that position
    if saved_stops[int(position)] != stop_id:
        # TODO show error about invalid data
        return
    new_stops_order = _reorder_stops_list(saved_stops, int(position), direction)
    await app_state.user_data_adapter.save_stops(chat_id, new_stops_order)

    await reorder_select_handler(update, context)
