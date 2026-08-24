from telegram.ext import Application
from bus_service.adapter import BusServiceAdapter
from storage.adapter import StorageUtility
from dataclasses import dataclass

STATE_KEY = "appstate"


@dataclass
class AppState:
    bus_service: BusServiceAdapter
    storage_utility: StorageUtility


def register_app_state(application: Application, app_state: AppState) -> None:
    application.bot_data[STATE_KEY] = app_state


def get_app_state(application: Application) -> AppState:
    return application.bot_data[STATE_KEY]
