import json
import logging
import time
from typing import Callable

from decouple import config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

from bus_arrival import get_arriving_busses
from bus_stops import GetNearestStops, GetStopInfo, nearest_stops_utility
from custom_typings import AllBusStops, BusStop
from format_message import make_next_bus_msg

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
        """Use the BusStopCode to get arrival timings for a particular stop.
e.g. 08031
You can also send your location to find the nearest stops
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


def button_handler(get_stop_info: GetStopInfo) -> Callable:
    """
    TODO describe
    """
    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query

        stop_id = query.data
        stop_info = get_stop_info(stop_id)
        busses = get_arriving_busses(stop_id)  # stop_id should never be None
        reply_msg = make_next_bus_msg(stop_info, busses, int(time.time()))

        await query.answer()
        await query.edit_message_text(text=reply_msg)

    return button


def message_handler(get_stop_info: GetStopInfo) -> Callable:
    """
    TODO describe
    """
    async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # check if user supplied a valid BusStopCode
        user_msg = update.message.text

        # invalid
        stop_info = get_stop_info(user_msg)
        if stop_info is None:
            await update.message.reply_text("Unknown bus stop code")
            return
        # valid
        busses = get_arriving_busses(user_msg)
        reply_msg = make_next_bus_msg(stop_info, busses, int(time.time()))
        await update.message.reply_text(reply_msg)
    return message


def init() -> tuple[GetNearestStops, GetStopInfo]:
    """initializes application state"""
    with open("bus_stops.json") as f:
        all_stops: AllBusStops = json.loads(f.read())
        bus_stops = all_stops["bus_stops"]
        return nearest_stops_utility(bus_stops)


def main() -> None:
    """Start the bot."""
    # Init application state
    get_nearest_stops, get_stop_info = init()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config("BOT_TOKEN")).build()

    # on different commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))

    # on non command i.e message
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, message_handler(get_stop_info)))
    application.add_handler(MessageHandler(
        filters.LOCATION, location_handler(get_nearest_stops)))
    application.add_handler(CallbackQueryHandler(
        button_handler(get_stop_info)))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()