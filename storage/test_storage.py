"""
https://www.sqlite.org/inmemorydb.html
"""

import pytest
import pytest_asyncio

from .adapter import StorageUtility


@pytest_asyncio.fixture
async def storage_utility():
    storage_utility = await StorageUtility.create(in_memory=True)
    await storage_utility.add_user(123456)
    return storage_utility


@pytest.mark.asyncio
async def test_save_0_stops(storage_utility: StorageUtility):
    """
    add 0 stops
    """
    await storage_utility.save_stops(123456, [])
    stops = await storage_utility.get_saved_stops(123456)
    assert stops == []


@pytest.mark.asyncio
async def test_save_1_stop(storage_utility: StorageUtility):
    """
    add 1 stop
    """
    await storage_utility.save_stops(123456, ["123456"])
    stops = await storage_utility.get_saved_stops(123456)
    assert stops == ["123456"]


@pytest.mark.asyncio
async def test_update_stop(storage_utility: StorageUtility):
    """
    add 1 stop and update
    """
    await storage_utility.save_stops(123456, ["123456"])
    await storage_utility.save_stops(123456, ["222", "333", "444"])
    stops = await storage_utility.get_saved_stops(123456)
    assert stops == ["222", "333", "444"]


@pytest.mark.asyncio
async def test_nonexistent_user(storage_utility: StorageUtility):
    """
    check if able to query for non-existent user
    """
    await storage_utility.save_stops(123456, ["123456"])
    stops = await storage_utility.get_saved_stops(999111)
    assert stops == None


@pytest.mark.asyncio
async def test_nonexistent_user_add_stop(storage_utility: StorageUtility):
    """
    check if able to query for non-existent user
    """
    assert await storage_utility.save_stops(999111, ["123456"]) == False
    assert await storage_utility.get_saved_stops(123456) == []


@pytest.mark.asyncio
async def test_check_user_exists(storage_utility: StorageUtility):
    """
    check if user exists
    """
    assert await storage_utility.check_user_exists(123456) == True
    assert await storage_utility.check_user_exists(999999) == False


@pytest.mark.asyncio
async def test_check_default_user_settings_exist(storage_utility: StorageUtility):
    user_settings = await storage_utility.get_user_settings(123456)
    assert user_settings is not None
    assert user_settings.show_load == False and user_settings.show_type == False


@pytest.mark.asyncio
async def test_modify_user_settings(storage_utility: StorageUtility):
    await storage_utility.save_user_settings(123456, True, False)
    user_settings = await storage_utility.get_user_settings(123456)
    assert user_settings is not None
    assert user_settings.show_load == True and user_settings.show_type == False
