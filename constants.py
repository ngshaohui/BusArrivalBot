from enum import Enum


class SETTINGS_ACTIONS(Enum):
    """
    Enum for settings callback states
    """

    SHOW = "SETTINGS_SHOW"
    ADD = "SETTINGS_ADD"  # TODO: remove if unused
    REMOVE = "SETTINGS_REMOVE"
    ADD_FLOW = "SETTINGS_ADD_FLOW"  # TODO: remove if unused
    REMOVE_FLOW = "SETTINGS_REMOVE_FLOW"
    REORDER = "SETTINGS_REORDER"
    CONSENT = "SETTINGS_CONSENT"
    DECLINE = "SETTINGS_DECLINE"
    DECLINE_CONFIRM = "SETTINGS_DECLINE_CONFIRM"
