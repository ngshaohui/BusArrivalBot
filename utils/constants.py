from enum import Enum

APP_VERSION = "0.3.0"


class SETTINGS_ACTIONS(Enum):
    """
    Enum for settings callback states
    """

    SHOW = "SETTINGS_SHOW"
    REMOVE_FLOW = "SETTINGS_REMOVE_FLOW"
    REMOVE = "SETTINGS_REMOVE"
    REORDER_FLOW = "SETTINGS_REORDER_FLOW"
    REORDER_SELECT = "SETTINGS_REORDER_SELECT"
    REORDER = "SETTINGS_REORDER"
    CONSENT = "SETTINGS_CONSENT"
    DECLINE_FLOW = "SETTINGS_DECLINE_FLOW"
    DECLINE = "SETTINGS_DECLINE"
    SYMBOL_SHOW = "SETTINGS_SYMBOL_SHOW"


SYMBOLS_LEGEND = """Legend
🟢 - Seats, 🟡 - Standing, 🔴 - Limited Standing
DD - Double Decker, BD - Bendy Bus
"""
