import json
import logging
import time
from typing import Callable

from decouple import config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

from bus_arrival import get_arriving_busses
from bus_stops import GetNearestStops, GetStopInfo, SearchPossibleStops
from custom_typings import AllBusRoutes, AllBusStops, BusStop
from format_message import bus_stop_search_msg, next_bus_msg, bus_route_msg
from service_integrator import GetRouteStops, init_integrator

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        f"""Use the BusStopCode to get arrival timings for a particular stop.
e.g. 08031

You can also send your location to find the nearest stops!

{config("VERSION")}
"""
    )


def location_handler(get_nearest_stops: GetNearestStops) -> Callable:
    """
    send prompt for users to select nearest bus stop (out of 3 candidates)
    """
    def get_stop_inline_button(bus_stop: BusStop) -> list[InlineKeyboardButton]:
        return [
            InlineKeyboardButton(f"{bus_stop['BusStopCode']} | {bus_stop['Description']}",
                                 callback_data=bus_stop["BusStopCode"])
        ]

    async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # get nearest stops
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        nearest_stops: list[BusStop] = get_nearest_stops((latitude, longitude))

        # build keyboard
        keyboard = list(map(get_stop_inline_button, nearest_stops))
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Here are the 3 closest bus stops:",
            reply_markup=reply_markup)
    return location


def make_refresh_button(stop_id: str) -> list[list[InlineKeyboardButton]]:
    "button to refresh arrival timings"
    return [[
        InlineKeyboardButton(f"Refresh", callback_data=stop_id)
    ]]


def button_handler(get_stop_info: GetStopInfo) -> Callable:
    """
    get button selection callback handler
    """
    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query
        stop_id = query.data

        # craft message
        stop_info = get_stop_info(stop_id)
        if stop_info is None:
            await update.message.reply_text("Unknown bus stop code")
            return
        busses = get_arriving_busses(stop_id)  # stop_id should never be None
        reply_msg = next_bus_msg(stop_info, busses, int(time.time()))

        # refresh button
        reply_markup = InlineKeyboardMarkup(make_refresh_button(stop_id))

        try:
            await query.answer()
            await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
        except BadRequest:
            # ignore error messages caused by repeated messages to mute errors
            pass

    return button


def message_handler(get_stop_info: GetStopInfo) -> Callable:
    """
    get handler for user supplied text messages
    """
    async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # check if user supplied a valid BusStopCode
        user_stop_id = update.message.text

        # user_stop_id is invalid
        stop_info = get_stop_info(user_stop_id)
        if stop_info is None:
            await update.message.reply_text("Unknown bus stop code")
            return

        # craft message
        busses = get_arriving_busses(user_stop_id)
        reply_msg = next_bus_msg(stop_info, busses, int(time.time()))

        # refresh button
        reply_markup = InlineKeyboardMarkup(make_refresh_button(user_stop_id))

        await update.message.reply_text(reply_msg, reply_markup=reply_markup)
    return message


def search_handler(search_possible_stops: SearchPossibleStops) -> Callable:
    """
    get button selection callback handler
    """
    async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message text."""
        search_query = context.args

        # craft message
        possible_stops = search_possible_stops(search_query)
        reply_msg = bus_stop_search_msg(possible_stops)

        await update.message.reply_text(text=reply_msg)

    return search


def bus_stop_code_handler(get_stop_info: GetStopInfo) -> Callable:
    """
    get handler for pseudo bus stop code commands
    """
    async def bus_stop_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message text."""
        full_text = update.message.text
        stop_id = full_text.split()[0].split('/')[1]

        # craft message
        stop_info = get_stop_info(stop_id)
        if stop_info is None:
            await update.message.reply_text("Unknown bus stop code")
            return
        busses = get_arriving_busses(stop_id)
        reply_msg = next_bus_msg(stop_info, busses, int(time.time()))

        # refresh button
        reply_markup = InlineKeyboardMarkup(make_refresh_button(stop_id))

        await update.message.reply_text(text=reply_msg, reply_markup=reply_markup)

    return bus_stop_code


def make_change_route_btn(bus_number: str, direction: int) -> list[list[InlineKeyboardButton]]:
    "button to refresh arrival timings"
    return [[
        InlineKeyboardButton(
            f"Change direction", callback_data=f"{bus_number},{direction}")
    ]]


def bus_route_handler(get_route_stops: GetRouteStops) -> Callable:
    """
    get handler for getting bus route information
    """
    async def bus_route(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if context.args is None:
            await update.message.reply_text("Please provide a bus number")
            return

        bus_number = context.args[0]

        # craft message
        route_info = get_route_stops(bus_number, 1)
        if route_info is None:
            await update.message.reply_text("Unknown bus number")
            return
        reply_msg = bus_route_msg(bus_number, route_info)

        # refresh button
        reply_markup = InlineKeyboardMarkup(
            make_change_route_btn(bus_number, 2))

        await update.message.reply_text(text=reply_msg, reply_markup=reply_markup)

    return bus_route


def route_direction_handler(get_route_stops: GetRouteStops) -> Callable:
    """
    get change route direction button selection callback handler
    """
    async def route_direction_handler_button(
            update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        gives the route for the other direction
        """
        query = update.callback_query
        if query.data is None:
            # ignore malformed requests
            return
        bus_number, direction_str = query.data.split(',')

        # craft message
        route_info = get_route_stops(bus_number, int(direction_str))
        if route_info is None:
            await update.message.reply_text("Unknown bus number")
            return
        reply_msg = bus_route_msg(bus_number, route_info)

        # refresh button
        reply_markup = InlineKeyboardMarkup(
            make_change_route_btn(bus_number, 1 if direction_str == "2" else 2))

        try:
            await query.answer()
            await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
        except BadRequest:
            # ignore error messages caused by repeated messages to mute errors
            pass

    return route_direction_handler_button


def init() -> tuple[GetNearestStops, GetStopInfo, SearchPossibleStops, GetRouteStops]:
    """initializes application state"""
    with open("bus_stops.json") as f1, open("bus_routes.json") as f2:
        all_stops: AllBusStops = json.loads(f1.read())
        bus_stops = all_stops["bus_stops"]
        all_routes: AllBusRoutes = json.loads(f2.read())
        bus_routes = all_routes["bus_routes"]
        return init_integrator(bus_routes, bus_stops)


def main() -> None:
    """Start the bot."""
    # Init application state
    get_nearest_stops, get_stop_info, search_possible_stops, get_route_stops = init()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config("BOT_TOKEN")).build()

    # on different commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler(
        "search", search_handler(search_possible_stops)))
    application.add_handler(CommandHandler(
        "route", bus_route_handler(get_route_stops)
    ))

    # add psuedo command to handle BusStopCode e.g. /08031
    for i in range(99999 + 1):
        application.add_handler(CommandHandler(
            f'{i:05}', bus_stop_code_handler(get_stop_info)))

    # on non command i.e message
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, message_handler(get_stop_info)))
    application.add_handler(MessageHandler(
        filters.LOCATION, location_handler(get_nearest_stops)))
    application.add_handler(CallbackQueryHandler(button_handler(get_stop_info),
                                                 pattern=r"\d{5}"))
    application.add_handler(CallbackQueryHandler(route_direction_handler(get_route_stops),
                                                 pattern=r"\d{1,3}\w?\,[12]"))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
