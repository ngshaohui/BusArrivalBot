import time
from typing import Callable

from telegram import InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bus_arrival import get_arriving_busses
from bus_stops import GetStopInfo
from format_message import bus_route_msg, next_bus_msg
from service_integrator import GetRouteStops
from .inline_buttons import make_change_route_btn, make_refresh_button


def route_direction_handler(get_route_stops: GetRouteStops) -> Callable:
    async def route_direction_handler_button(
            update: Update,
            _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        gives the route for the other direction
        """
        query = update.callback_query
        if query is None or query.data is None:
            # ignore malformed requests
            return
        bus_number, direction_str = query.data.split(',')

        # craft message
        route_info = get_route_stops(bus_number, int(direction_str))
        if route_info is None:
            await query.edit_message_text("Unknown bus number")
            return
        reply_msg = bus_route_msg(bus_number, route_info)

        # refresh button
        reply_markup = InlineKeyboardMarkup(
            make_change_route_btn(bus_number, 1 if direction_str == "2" else 2))

        await query.answer()
        try:
            await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
        except BadRequest:
            # ignore errors due to same message being sent
            pass
    return route_direction_handler_button


def bus_number_handler(get_stop_info: GetStopInfo) -> Callable:
    """
    get button selection callback handler
    """
    async def button(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query
        if query is None or query.data is None:
            # ignore malformed requests
            return
        stop_id = query.data

        # craft message
        stop_info = get_stop_info(stop_id)
        if stop_info is None:
            await query.edit_message_text("Unknown bus stop code")
            return
        busses = get_arriving_busses(stop_id)  # stop_id should never be None
        reply_msg = next_bus_msg(stop_info, busses, int(time.time()))

        # refresh button
        reply_markup = InlineKeyboardMarkup(make_refresh_button(stop_id))

        await query.answer()
        try:
            await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
        except BadRequest:
            # ignore errors due to same message being sent
            pass

    return button
