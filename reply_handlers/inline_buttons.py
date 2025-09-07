from telegram import InlineKeyboardButton

from custom_typings import BusStop


def make_change_route_btn(
    bus_number: str, direction: int
) -> list[list[InlineKeyboardButton]]:
    "button to refresh arrival timings"
    return [
        [
            InlineKeyboardButton(
                "Change direction", callback_data=f"{bus_number},{direction}"
            )
        ]
    ]


def make_refresh_button(stop_id: str) -> list[list[InlineKeyboardButton]]:
    "button to refresh arrival timings"
    return [[InlineKeyboardButton("Refresh", callback_data=stop_id)]]


def get_stop_inline_button(bus_stop: BusStop) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            f"{bus_stop['BusStopCode']} | {bus_stop['Description']}",
            callback_data=bus_stop["BusStopCode"],
        )
    ]
