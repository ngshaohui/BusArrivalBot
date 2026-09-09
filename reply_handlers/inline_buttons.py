from telegram import InlineKeyboardButton

from utils.custom_typings import BusStop


def get_stop_inline_button(bus_stop: BusStop) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            f"{bus_stop['BusStopCode']} | {bus_stop['Description']}",
            callback_data=bus_stop["BusStopCode"],
        )
    ]
