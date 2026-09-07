"""
https://www.sqlite.org/inmemorydb.html
"""

import pytest

from .adapter import StorageUtility


@pytest.fixture
def storage_utility():
    storage_utility = StorageUtility(in_memory=True)
    storage_utility.add_user(123456)
    return storage_utility


def test_save_0_stops(storage_utility: StorageUtility):
    """
    add 0 stops
    """
    storage_utility.save_stops(123456, [])
    stops = storage_utility.get_saved_stops(123456)
    assert stops == []


def test_save_1_stop(storage_utility: StorageUtility):
    """
    add 1 stop
    """
    storage_utility.save_stops(123456, ["123456"])
    stops = storage_utility.get_saved_stops(123456)
    assert stops == ["123456"]


def test_update_stop(storage_utility: StorageUtility):
    """
    add 1 stop and update
    """
    storage_utility.save_stops(123456, ["123456"])
    storage_utility.save_stops(123456, ["222", "333", "444"])
    stops = storage_utility.get_saved_stops(123456)
    assert stops == ["222", "333", "444"]


def test_nonexistent_user(storage_utility: StorageUtility):
    """
    check if able to query for non-existent user
    """
    storage_utility.save_stops(123456, ["123456"])
    stops = storage_utility.get_saved_stops(999111)
    assert stops == []


def test_nonexistent_user_add_stop(storage_utility: StorageUtility):
    """
    check if able to query for non-existent user
    """
    assert storage_utility.save_stops(999111, ["123456"]) == False
    assert storage_utility.get_saved_stops(123456) == []


def test_check_user_exists(storage_utility: StorageUtility):
    """
    check if user exists
    """
    assert storage_utility.check_user_exists(123456) == True
    assert storage_utility.check_user_exists(999999) == False


def test_check_default_user_settings_exist(storage_utility: StorageUtility):
    user_settings = storage_utility.get_user_settings(123456)
    assert user_settings.show_load == False and user_settings.show_type == False


def test_modify_user_settings(storage_utility: StorageUtility):
    storage_utility.save_user_settings(123456, True, False)
    user_settings = storage_utility.get_user_settings(123456)
    assert user_settings.show_load == True and user_settings.show_type == False
