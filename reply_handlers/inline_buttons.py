from telegram import InlineKeyboardButton


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
