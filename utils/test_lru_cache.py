from freezegun import freeze_time
import pytest

from lru_cache import LRUCache


def test_key_existence():
    cache = LRUCache(ttl=1, item_limit=10)
    cache.set("a", 1)
    assert cache.get("a") == 1
    assert cache.get("b") is None


def test_eviction():
    """
    item limit of 2
    """
    cache = LRUCache(ttl=1, item_limit=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3


def test_expiry():
    with freeze_time() as frozen_datetime:
        cache = LRUCache(ttl=1, item_limit=5)
        cache.set("a", 1)
        frozen_datetime.tick(2)
        assert cache.get("a") is None  # should expire


def test_get_updates_lru_order():
    cache = LRUCache(ttl=10, item_limit=2)
    cache.set("a", 1)
    cache.set("b", 2)
    # make "a" most recently used
    assert cache.get("a") == 1
    cache.set("c", 3)
    # cache should only contain "a" and "c"
    # "b" evicted due to item limit
    assert cache.get("a") == 1
    assert cache.get("b") is None
    assert cache.get("c") == 3


def test_overwrite_key_resets_ttl():
    with freeze_time() as frozen_datetime:
        cache = LRUCache(ttl=3, item_limit=10)
        cache.set("a", 1)
        frozen_datetime.tick(2)
        cache.set("a", 2)
        frozen_datetime.tick(2)
        # second insert refreshes expiry
        assert cache.get("a") == 2


def test_multiple_types():
    cache = LRUCache(ttl=5, item_limit=5)
    cache.set("int", 123)
    cache.set("str", "hello")
    cache.set("list", [1, 2, 3])
    assert cache.get("int") == 123
    assert cache.get("str") == "hello"
    assert cache.get("list") == [1, 2, 3]


def test_eviction_respects_item_limit():
    limit = 10
    cache = LRUCache(ttl=10, item_limit=limit)
    for i in range(limit * 2):  # insert double the limit
        cache.set(f"k{i}", i)
    assert len(cache.item_cache) == limit


def test_none_values_are_allowed():
    cache = LRUCache(ttl=5, item_limit=5)
    cache.set("a", None)
    assert cache.get("a") is None
    # must still exist in cache
    assert "a" in cache.item_cache


@pytest.mark.parametrize("ttl", [1, 2, 3])
def test_parametrized_ttl(ttl):
    with freeze_time() as frozen_datetime:
        cache = LRUCache(ttl=ttl, item_limit=2)
        cache.set("a", "value")
        frozen_datetime.tick(ttl + 1)
        assert cache.get("a") is None
