from telegram import InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from message_formatters.bus_route import bus_route_msg

from .inline_buttons import make_change_route_btn


async def route_direction_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    gives the route for the other direction
    """
    query = update.callback_query
    if query is None or query.data is None:
        # ignore malformed requests
        return
    bus_number, direction_str = query.data.split(",")

    # craft message
    app_state = get_app_state(context.application)
    route_info = app_state.bus_service.get_route_stops(bus_number, int(direction_str))
    if route_info is None:
        await query.edit_message_text("Unknown bus number")
        return
    reply_msg = bus_route_msg(bus_number, route_info)

    # refresh button
    reply_markup = InlineKeyboardMarkup(
        make_change_route_btn(bus_number, 1 if direction_str == "2" else 2)
    )

    await query.answer()
    try:
        await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
    except BadRequest:
        # ignore errors due to same message being sent
        pass
