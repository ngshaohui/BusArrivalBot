from telegram import InlineKeyboardButton

from utils.constants import SETTINGS_ACTIONS
from utils.custom_typings import BusStop


def get_stop_inline_button(bus_stop: BusStop) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            f"{bus_stop['BusStopCode']} | {bus_stop['Description']}",
            callback_data=bus_stop["BusStopCode"],
        )
    ]


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
    [
        InlineKeyboardButton(
            "Show symbols", callback_data=SETTINGS_ACTIONS.SYMBOL_SHOW.value
        )
    ],
]
