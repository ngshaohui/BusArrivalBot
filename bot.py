import json
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot_app_state import AppState, get_app_state, register_app_state
from bus_service.adapter import BusServiceAdapter
from reply_handlers.bus_arrival import REGEX_STOP_CODE, bus_stop_handler
from reply_handlers.bus_route import route_direction_handler
from reply_handlers.inline_buttons import get_stop_inline_button
from reply_handlers.settings_handler import (
    register_settings_handlers,
    show_settings_handler,
)
from reply_handlers.text_reply_handler import message_handler
from scripts import fetch_routes, fetch_stops
from storage.adapter import StorageUtility
from user_data.adapter import UserDataAdapter
from utils.constants import APP_VERSION
from utils.custom_typings import BusRoute, BusStop

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

DEVELOPMENT_MODE = config("DEVELOPMENT_MODE", default=False, cast=bool)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        f"""Use the BusStopCode to get arrival timings for a particular stop
`08031`

View the list of bus routes along the bus stop with the bus number
`170`

Save the BusStopCode for quick access and view the list of saved stops with /list
`add 08031`

You can also send your location to find the nearest stops!

v{APP_VERSION}""",
        parse_mode="Markdown",
    )


async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.location is None:
        return
    # get nearest stops
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    app_state = get_app_state(context.application)
    nearest_stops: list[BusStop] = app_state.bus_service.get_nearest_stops(
        (latitude, longitude), 3
    )

    # build keyboard
    keyboard = list(map(get_stop_inline_button, nearest_stops))
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Here are the 3 closest bus stops:", reply_markup=reply_markup
    )


def fetch_stops_and_routes(
    development_mode: bool = False,
) -> tuple[list[BusStop], list[BusRoute]]:
    """
    Fetches bus stops and routes data.
    """
    if development_mode:
        with open("bus_stops.json") as f1, open("bus_routes.json") as f2:
            bus_stops: list[BusStop] = json.load(f1)["bus_stops"]
            bus_routes: list[BusRoute] = json.load(f2)["bus_routes"]
        logger.info("Load data from local filesystem")
    else:
        bus_stops = fetch_stops.run()
        bus_routes = fetch_routes.run()
        logger.info("Fetched latest data from LTA API")
    return bus_stops, bus_routes


def refresh_bus_service_adapter(bus_service_adapter: BusServiceAdapter):
    """refreshes the service integrator"""

    def refresh() -> None:
        bus_service_adapter.refresh(*fetch_stops_and_routes())

    return refresh


async def post_init(application: Application) -> None:
    # Init application state
    storage_utility = await StorageUtility.create(in_memory=DEVELOPMENT_MODE)
    bus_service_adapter = BusServiceAdapter(
        *fetch_stops_and_routes(development_mode=DEVELOPMENT_MODE)
    )
    user_data_adapter = UserDataAdapter(storage_utility)

    # Fetch new data once a week on Sundays
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        refresh_bus_service_adapter(bus_service_adapter),
        trigger="cron",
        day_of_week="sun",
        hour=0,
        minute=0,
    )
    scheduler.start()
    register_app_state(application, AppState(bus_service_adapter, user_data_adapter))


def main() -> None:
    """Start the bot."""

    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(config("BOT_TOKEN", cast=str))
        .post_init(post_init)
        .build()
    )

    # on different commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("settings", show_settings_handler))

    # on non command i.e message
    application.add_handler(MessageHandler(filters.TEXT, message_handler))
    application.add_handler(MessageHandler(filters.LOCATION, location_handler))
    application.add_handler(
        CallbackQueryHandler(bus_stop_handler, pattern=REGEX_STOP_CODE)
    )
    application.add_handler(
        CallbackQueryHandler(route_direction_handler, pattern=r"\d{1,3}\w?\,[12]")
    )
    # settings
    register_settings_handlers(application)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
