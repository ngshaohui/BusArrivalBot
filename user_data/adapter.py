import asyncio
from dataclasses import dataclass, field
from typing import NamedTuple

from storage.adapter import StorageUtility
from utils.custom_typings import UserSettings
from utils.lru_cache import LRUCache

SECONDS_IN_DAY = 86400


class _UserDoesNotExist:
    pass


USER_DOES_NOT_EXIST = _UserDoesNotExist()  # sentinel object


class UserData(NamedTuple):
    saved_stops: list[str]
    user_settings: UserSettings


class StripedLock:
    def __init__(self):
        self._locks = [asyncio.Lock() for _ in range(100)]

    def shared_lock(self, chat_id: int) -> asyncio.Lock:
        return self._locks[chat_id % 100]


@dataclass
class UserDataAdapter:
    storage_adapter: StorageUtility
    _user_data_cache: LRUCache[UserData | _UserDoesNotExist] = field(
        default_factory=lambda: LRUCache[UserData | _UserDoesNotExist](
            ttl=SECONDS_IN_DAY, item_limit=500
        )
    )
    _shared_key_locks: StripedLock = field(default_factory=StripedLock)

    async def get_user_data(
        self, chat_id: int, update_cache: bool = False
    ) -> UserData | _UserDoesNotExist:
        "all methods should call this first so that it can check and set the cache"
        user_data = self._user_data_cache.get(chat_id)
        if user_data is None or update_cache:
            # handle cache miss
            (saved_stops, user_settings) = await asyncio.gather(
                self.storage_adapter.get_saved_stops(chat_id),
                self.storage_adapter.get_user_settings(chat_id),
            )
            # both are either None or have valid data
            if saved_stops is not None and user_settings is not None:
                user_data = UserData(saved_stops, user_settings)
                self._user_data_cache.set(chat_id, user_data)
            else:
                user_data = USER_DOES_NOT_EXIST
                self._user_data_cache.set(chat_id, USER_DOES_NOT_EXIST)
        return user_data

    # user

    async def check_user_exists(self, chat_id: int) -> bool:
        user_data = await self.get_user_data(chat_id)
        return isinstance(user_data, UserData)

    async def add_user(self, chat_id: int):
        "idempotent if the user already exists"
        async with self._shared_key_locks.shared_lock(chat_id):
            user_data = await self.get_user_data(chat_id)
            if isinstance(user_data, UserData):
                return
            success = await self.storage_adapter.add_user(chat_id)
            if success:
                # update negative cache
                await self.get_user_data(chat_id, True)
            # TODO: handle error

    async def remove_user(self, chat_id: int):
        "idempotent if the user does not exists"
        async with self._shared_key_locks.shared_lock(chat_id):
            user_data = await self.get_user_data(chat_id)
            if isinstance(user_data, _UserDoesNotExist):
                return
            success = await self.storage_adapter.remove_user(chat_id)
            if success:
                # update negative cache
                self._user_data_cache.set(chat_id, USER_DOES_NOT_EXIST)
            # TODO: handle error

    # saved_stops

    async def get_saved_stops(self, chat_id: int) -> list[str]:
        user_data = await self.get_user_data(chat_id)
        if isinstance(user_data, UserData):
            return user_data.saved_stops
        return []

    async def add_stop(self, chat_id: int, stop_id: str):
        """
        idempotent if the user does not exist
        idempotent if stop already exists
        """
        async with self._shared_key_locks.shared_lock(chat_id):
            user_data = await self.get_user_data(chat_id)
            if isinstance(user_data, _UserDoesNotExist):
                return
            if stop_id in user_data.saved_stops:
                return
            new_saved_stops = user_data.saved_stops + [stop_id]
            success = await self.storage_adapter.save_stops(chat_id, new_saved_stops)
            if success:
                self._user_data_cache.set(
                    chat_id, UserData(new_saved_stops, user_data.user_settings)
                )
            # TODO: handle error

    async def save_stops(self, chat_id: int, stop_ids: list[str]):
        """
        idempotent if the user does not exist
        """
        async with self._shared_key_locks.shared_lock(chat_id):
            user_data = await self.get_user_data(chat_id)
            if isinstance(user_data, _UserDoesNotExist):
                return
            success = await self.storage_adapter.save_stops(chat_id, stop_ids)
            if success:
                self._user_data_cache.set(
                    chat_id, UserData(stop_ids, user_data.user_settings)
                )
            # TODO: handle error

    async def remove_stop(self, chat_id: int, stop_id: str):
        """
        idempotent if the user does not exist
        idempotent if stop does not exist
        """
        async with self._shared_key_locks.shared_lock(chat_id):
            user_data = await self.get_user_data(chat_id)
            if isinstance(user_data, _UserDoesNotExist):
                return
            saved_stops = user_data.saved_stops
            for idx, saved_stop_id in enumerate(saved_stops):
                if stop_id == saved_stop_id:
                    new_stop_ids = saved_stops[:idx] + saved_stops[idx + 1 :]
                    success = await self.storage_adapter.save_stops(
                        chat_id, new_stop_ids
                    )
                    if success:
                        self._user_data_cache.set(
                            chat_id, UserData(new_stop_ids, user_data.user_settings)
                        )
                    # TODO: handle error

    # user_settings

    async def get_user_settings(self, chat_id: int) -> UserSettings:
        user_data = await self.get_user_data(chat_id)
        if isinstance(user_data, UserData):
            return user_data.user_settings
        return UserSettings(False, False)  # default user settings

    async def save_user_settings(self, chat_id: int, show_load: bool, show_type: bool):
        """
        idempotent if the user does not exist
        """
        async with self._shared_key_locks.shared_lock(chat_id):
            user_data = await self.get_user_data(chat_id)
            if isinstance(user_data, _UserDoesNotExist):
                return
            success = await self.storage_adapter.save_user_settings(
                chat_id, int(show_load), int(show_type)
            )
            if success:
                self._user_data_cache.set(
                    chat_id,
                    UserData(user_data.saved_stops, UserSettings(show_load, show_type)),
                )
            # TODO: handle error
