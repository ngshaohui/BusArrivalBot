from collections import OrderedDict
from dataclasses import dataclass, field
import time
from typing import Generic, NamedTuple, TypeVar

T = TypeVar("T")


class CacheItem(NamedTuple, Generic[T]):
    value: T
    expiry: int


@dataclass
class LRUCache(Generic[T]):
    item_cache: OrderedDict[str, CacheItem[T]] = field(default_factory=OrderedDict)
    ttl: int = 20  # time in seconds
    item_limit: int = 100

    def __is_expired(self, item: CacheItem[T]) -> bool:
        return int(time.time()) > item.expiry

    def __touch(self, key: str) -> None:
        "re-insert key to update insertion order"
        item = self.item_cache.get(key, None)
        if item is not None:
            self.item_cache[key] = CacheItem(item.value, int(time.time()) + self.ttl)
            self.item_cache.move_to_end(key)

    def get(self, key: str) -> T | None:
        item = self.item_cache.get(key, None)
        if item is None:
            return None
        if self.__is_expired(item):
            del self.item_cache[key]
            return None
        self.__touch(key)
        return item.value

    def set(self, key: str, value: T) -> None:
        if key in self.item_cache:
            # remove old entry
            del self.item_cache[key]

        if len(self.item_cache) >= self.item_limit:
            # delete oldest item
            self.item_cache.popitem(last=False)

        # add item to cache
        self.item_cache[key] = CacheItem(value, int(time.time()) + self.ttl)
