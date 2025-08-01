import logging
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

from custom_typings import AllBusRoutes, AllBusStops, BusRoute, BusStop
from reply_handlers.callback_query_handler import bus_number_handler, route_direction_handler
from reply_handlers.text_reply_handler import message_handler
from scripts import fetch_routes, fetch_stops
from service_integrator import ServiceIntegrator

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        f"""Use the BusStopCode to get arrival timings for a particular stop.
e.g. 08031

You can also send your location to find the nearest stops!

{config("VERSION")}
"""
    )


def location_handler(service_integrator: ServiceIntegrator) -> Callable:
    """
    send prompt for users to select nearest bus stop (out of 3 candidates)
    """
    def get_stop_inline_button(bus_stop: BusStop) -> list[InlineKeyboardButton]:
        return [
            InlineKeyboardButton(f"{bus_stop['BusStopCode']} | {bus_stop['Description']}",
                                 callback_data=bus_stop["BusStopCode"])
        ]

    async def location(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        # workaround: pylint error suppression
        if update.message is None or update.message.location is None:
            return
        # get nearest stops
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        nearest_stops: list[BusStop] = service_integrator.get_nearest_stops(
            (latitude, longitude), 3)

        # build keyboard
        keyboard = list(map(get_stop_inline_button, nearest_stops))
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Here are the 3 closest bus stops:",
            reply_markup=reply_markup)
    return location


def fetch_stops_and_routes() -> tuple[list[BusStop], list[BusRoute]]:
    """Fetches bus stops and routes data."""
    all_stops: AllBusStops = fetch_stops.run()
    bus_stops = all_stops["bus_stops"]
    all_routes: AllBusRoutes = fetch_routes.run()
    bus_routes = all_routes["bus_routes"]
    return bus_stops, bus_routes


def refresh_service_integrator(service_integrator: ServiceIntegrator):
    """refreshes the service integrator"""
    def refresh() -> None:
        service_integrator.refresh(*fetch_stops_and_routes())
    return refresh


def main() -> None:
    """Start the bot."""
    # Init application state
    service_integrator = ServiceIntegrator(*fetch_stops_and_routes())
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_service_integrator(service_integrator),
                      trigger='cron',
                      day_of_week='sun',
                      hour=0,
                      minute=0)
    scheduler.start()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(
        config("BOT_TOKEN")).build()  # type: ignore

    # on different commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))

    # on non command i.e message
    application.add_handler(MessageHandler(
        filters.TEXT, message_handler(service_integrator)))
    application.add_handler(MessageHandler(
        filters.LOCATION, location_handler(service_integrator)))
    application.add_handler(CallbackQueryHandler(bus_number_handler(service_integrator),
                                                 pattern=r"\d{5}"))
    application.add_handler(CallbackQueryHandler(route_direction_handler(service_integrator),
                                                 pattern=r"\d{1,3}\w?\,[12]"))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
