import pytest
import pytest_asyncio

from storage.adapter import StorageUtility
from utils.custom_typings import UserSettings

from .adapter import UserDataAdapter

EXISTING_USER = 123456
NON_EXISTENT_USER = 654321


@pytest_asyncio.fixture
async def user_data_adapter():
    storage_utility = await StorageUtility.create(in_memory=True)
    user_data_adapter = UserDataAdapter(storage_utility)
    await user_data_adapter.add_user(EXISTING_USER)
    await user_data_adapter.save_user_settings(EXISTING_USER, True, False)
    return user_data_adapter


@pytest.mark.asyncio
async def test_user_exists(user_data_adapter: UserDataAdapter):
    assert await user_data_adapter.check_user_exists(EXISTING_USER)


@pytest.mark.asyncio
async def test_user_not_exists(user_data_adapter: UserDataAdapter):
    assert not await user_data_adapter.check_user_exists(NON_EXISTENT_USER)


@pytest.mark.asyncio
async def test_remove_user(user_data_adapter: UserDataAdapter):
    await user_data_adapter.remove_user(EXISTING_USER)
    assert not await user_data_adapter.check_user_exists(EXISTING_USER)


@pytest.mark.asyncio
async def test_remove_non_existent_user(user_data_adapter: UserDataAdapter):
    "test idempotent operation"
    await user_data_adapter.remove_user(NON_EXISTENT_USER)
    assert not await user_data_adapter.check_user_exists(NON_EXISTENT_USER)


@pytest.mark.asyncio
async def test_get_stop_non_existent_user(user_data_adapter: UserDataAdapter):
    stops = await user_data_adapter.get_saved_stops(NON_EXISTENT_USER)
    assert stops == []


@pytest.mark.asyncio
async def test_save_0_stops(user_data_adapter: UserDataAdapter):
    await user_data_adapter.save_stops(EXISTING_USER, [])
    stops = await user_data_adapter.get_saved_stops(EXISTING_USER)
    assert stops == []


@pytest.mark.asyncio
async def test_save_multiple_stops(user_data_adapter: UserDataAdapter):
    await user_data_adapter.save_stops(EXISTING_USER, ["1", "2", "3"])
    stops = await user_data_adapter.get_saved_stops(EXISTING_USER)
    assert stops == ["1", "2", "3"]


@pytest.mark.asyncio
async def test_add_1_stop(user_data_adapter: UserDataAdapter):
    await user_data_adapter.add_stop(EXISTING_USER, "222777")
    stops = await user_data_adapter.get_saved_stops(EXISTING_USER)
    assert stops == ["222777"]


@pytest.mark.asyncio
async def test_add_2_stops(user_data_adapter: UserDataAdapter):
    await user_data_adapter.add_stop(EXISTING_USER, "222777")
    await user_data_adapter.add_stop(EXISTING_USER, "333444")
    stops = await user_data_adapter.get_saved_stops(EXISTING_USER)
    assert stops == ["222777", "333444"]


@pytest.mark.asyncio
async def test_add_duplicate_stops(user_data_adapter: UserDataAdapter):
    await user_data_adapter.add_stop(EXISTING_USER, "222777")
    await user_data_adapter.add_stop(EXISTING_USER, "222777")
    stops = await user_data_adapter.get_saved_stops(EXISTING_USER)
    assert stops == ["222777"]


@pytest.mark.asyncio
async def test_add_stop_non_existent_user(user_data_adapter: UserDataAdapter):
    "test idempotent operation"
    await user_data_adapter.add_stop(NON_EXISTENT_USER, "222777")
    stops = await user_data_adapter.get_saved_stops(NON_EXISTENT_USER)
    assert stops == []


@pytest.mark.asyncio
async def test_add_and_remove_stop(user_data_adapter: UserDataAdapter):
    await user_data_adapter.add_stop(EXISTING_USER, "222777")
    await user_data_adapter.add_stop(EXISTING_USER, "333444")
    await user_data_adapter.remove_stop(EXISTING_USER, "222777")
    stops = await user_data_adapter.get_saved_stops(EXISTING_USER)
    assert stops == ["333444"]


@pytest.mark.asyncio
async def test_get_user_settings(
    user_data_adapter: UserDataAdapter,
):
    "data set up by fixture UserSettings(True, False)"
    user_settings = await user_data_adapter.get_user_settings(EXISTING_USER)
    assert user_settings == UserSettings(True, False)


@pytest.mark.asyncio
async def test_get_user_settings_non_existent_user(
    user_data_adapter: UserDataAdapter,
):
    "should give default UserSettings(False, False)"
    user_settings = await user_data_adapter.get_user_settings(NON_EXISTENT_USER)
    assert user_settings == UserSettings(False, False)


@pytest.mark.asyncio
async def test_change_user_settings(
    user_data_adapter: UserDataAdapter,
):
    "idempotent, should give default UserSettings(False, False)"
    await user_data_adapter.save_user_settings(EXISTING_USER, True, True)
    user_settings = await user_data_adapter.get_user_settings(EXISTING_USER)
    assert user_settings == UserSettings(True, True)


@pytest.mark.asyncio
async def test_change_user_settings_non_existent_user(
    user_data_adapter: UserDataAdapter,
):
    "idempotent, should give default UserSettings(False, False)"
    await user_data_adapter.save_user_settings(NON_EXISTENT_USER, True, True)
    user_settings = await user_data_adapter.get_user_settings(NON_EXISTENT_USER)
    assert user_settings == UserSettings(False, False)
