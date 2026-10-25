# Upgrading a 2017 project in 2024

This is meant to document the process of upgrading this project that was built back when I first started picking up coding.

It was originally built to be hosted on heroku, alongside the NUS version of it. Both bots were taken down sometime in 2019 due to the lack of time to keep up with the API changes, and I've decided to take pick this one up again since I've started taking busses more often.

This project seems to be hard to upgrade incrementally due to how monolithic it is, making it hard to replace its components. I'm not even sure if the libraries are still able to support all the function calls, at least not for the python telegram bot which is the main component in this project, since I adopted it in its infancy.

## Dependency management

The first change will be to move away from using `pip` and `requirements.txt` to manage dependencies to use `pipenv` instead, as this would bring me closer to a `package.json` experience.

## Modularisation

A good approach will be to try to replicate the functionality by splitting the code into multiple components.

0. telegram bot (core)
1. build KD-tree
2. message formatting (show something nice to user)
3. search for bus stop in kd-tree

## Storing the list of bus stops

Can consider 2 ways of loading bus stops
First way is to load from a json file, second way is to fetch from the API
The second way is bound to incur a lot of requests to the API
Consider that the list of bus stops also do not get updated much
Could explore generating some sort of checksum to indicate if the list of bus stops needs to be updated
Otherwise it's sufficient to keep loading from a json file.

Previous method would assume only 50 stops can be fetched at a time
However new method fetches 500 at a time
This meant that the old method was broken as it would re-fetch the same bus stops within the 500

The skip parameter has been documented in the API, but it does not indicate if you can restrict how many to fetch at any given time (most likely have to splice the list yourself)

## kd-tree

https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.query.html

The scipy library has a kd-tree, so there is no need to maintain a kd-tree implementation for nearest neighbour search

## formatting

having trouble with autopep8

vscode terminal reports a different version from the one installed using pipenv

## Rate limiting

Need a way to limit the amount of times someone can request for an update for bus stop information

The intention is to not make too many API requests to LTA Datamall

possible to write a decorator to ensure that a person has not sent too many messages (perhaps limiting at 1 message every 5 seconds)

Need to be careful that this does not interfere with the location -> button -> stop info flow, perhaps that one flow can possibly be exempt from rate limiting

Can also consider limiting the mechanism that makes the API call itself, as well as implement some form of cache layer for the requests

### Cache layer for API calls

Opted to implement a custom caching layer for the API calls

This should be better than keeping track of who-requests-for-what to rate limit their requests individually, as this has much more complicated state management

On top of that, caching at the API level also allows multiple unique individuals to tap on the same cache

```python
class BusInfoCacheItem(NamedTuple):
    retrieved: int
    busses: list[BusInfo]


# custom cache implementation
CACHE_EXPIRY = 20  # seconds
type CacheLayer = dict[str, BusInfoCacheItem]
__bus_info_cache: CacheLayer = {}
```

If a BusStopCode has been fetched within the past 20 seconds, the cached results will be used to prevent repeat API calls to the LTA Datamall endpoint

However, the flaw is that data leaks occur without a job to clear the cache regularly

Can consider scheduling a job to invalidate the cache every 30 minutes by calling `dict.clear()`

## Search bus stops

Can consider using aho corasick
https://github.com/WojciechMula/pyahocorasick

Decided not to add complicated logic for now, will just tokenise the stops for a string search

## Bus route

```python
class BusRoute(TypedDict):
    ServiceNo: str
    Direction: int
    StopSequence: int
    BusStopCode: str
    Distance: int
    WD_FirstBus: str
    WD_LastBus: str
    SAT_FirstBus: str
    SAT_LastBus: str
    SUN_FirstBus: str
    SUN_LastBus: str
```

```
/route 67

Bus 67 route

Choa Chu Kang Int /44009
Blk 352 /44461
...
Blk 414 /44469
Choa Chu Kang Int /44009
```

The bus stops however are within the file `bus_stops.py`

Might want to pass the search stops object/function into the `bus_route.py`?

Or possibly create a composed function

## Parsing inputs

Slash `/` commands are not very intuitive when they require an argument, as telegram lists the registered / commands which can be tapped to be sent out as a message without an argument.

`/search choa chu kang`

It may be more intuitive to type a search string directly

```
search choa chu kang
choa chu kang
```

## DB

Would have used template strings out of habit

Did not realise that tuples can be created with dangling commas

```python
# Don't do
cur.execute(f"SELECT * FROM saved_stops WHERE chat_id = {chat_id}")
# Do
cur.execute("SELECT * FROM saved_stops WHERE chat_id = ?", (chat_id,))
```

https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders

## Dependency management again

I ended up choosing `uv` as the package manager of choice. Seems to be the most intuitive and unopinionated one.

## Text vs Callback handlers

There is no need to differentiate between the 2, as it's possible for the function to handle both messages and callback queries

This is the case of the route direction, where the initial one is triggered from a message and the subsequent one triggered using a reply markup keyboard button

## LRU Cache

Was tasked to implement a LRU during one of my interviews, so I ended up using what I had written for that within this application after all to replace the previous `BusInfoCacheItem` that has unbounded memory use (well not exactly as it's still limited to the total of bus stops, but it's mostly unnecessary to cache everything).

When I tried to generate some of the test cases with ChatGPT, I realised that it was overly verbose with a lot of overlapping test cases.

Have opted to keep most of them, removing the more verbose ones.

## Deplying without docker

To allow usage of uv from the service account `pybotrunner`
Using the main account to do `uv sync` will cause the .venv to symlink to the user's home dir's python instead which `pybotrunner` doesn't have access to.
The solution is to create a service directory for `pybotrunner`.

```bash
sudo -u pybotrunner git pull

sudo mkdir -p /var/lib/pybotrunner
sudo chown pybotrunner:pybotrunner /var/lib/pybotrunner
sudo usermod -d /var/lib/pybotrunner pybotrunner

sudo -u pybotrunner -H sh -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
sudo -u pybotrunner -H /var/lib/pybotrunner/.local/bin/uv sync --locked --no-dev
```

## Async

Since `requests` http calls are synchronous, it blocks the thread while fetching bus arrival information so the next user calling the `bus_stop_handler` cannot be processed. It'll be quite apt to replace it with the httpx library instead for `httpx.AsyncClient()`.

This allows the async `bus_stop_handler` to properly make use of being an async function.

Next would be to use an async sqlite library.

This also allows us to simultaneously (1) make a http request to get bus arrival timings and (2) retrieve the user settings from the DB.

```py
(busses, user_settings) = await asyncio.gather(
    get_arriving_busses(stop_id),
    app_state.storage_utility.get_user_settings(chat_id),
)
```

### Async class instantiation

Since `aiosqlite.connect` is now an async call, the `StorageUtility` can no longer initiate the connection from its `__init__` constructor.

The workaround for this is to use an async `@classmethod` to move the async functions into, which subsequently calls the `__init__` constructor.

```py
class StorageUtility:
    def __init__(self, con: aiosqlite.Connection):
        logger.info("Using specified database connection")
        self.con: aiosqlite.Connection = con

    @classmethod
    async def create(cls, in_memory: bool = False) -> "StorageUtility":
        if in_memory:
            logger.info("Initializing new database from memory")
            con = await aiosqlite.connect("file::memory:", uri=True)
            await init(con)

        else:
            logger.info("Using database file bus_arrival_bot.db")
            con = await aiosqlite.connect("bus_arrival_bot.db")

        await con.execute("PRAGMA foreign_keys = ON;")
        await raise_if_table_not_init(con)

        return cls(con)
```

An alternative would have been to have an explicit method that needs to be called to initialize the connections, but this runs into the danger of being an antipattern since it's not intuitive that it needs to be done right after instantiation.

### Race conditions

Introducing async to aspects such as the DB also means making it susceptable to race conditions now.

Will need to look at implementing semaphores for write flows.

I think it'll be quite hard to trigger these race conditions given that the interface is a telegram bot, but the possibility is non-zero so this will need to be tackled at some point.

## Caching

Each command handler currently interfaces with the `app_state.storage_utility` directly to retrieve the `user_settings` from the DB.

This should be moved to an adapter under `user_data` instead.

This also allows the `user_settings` to be cached within the `user_data` module, as it wouldn't make sense to cache directly within the `storage_utility` DB adapter.

### Negative cache

The caching strategy is a negative cache, which also keeps track of which users are not found within the database.

```py
class _UserDoesNotExist:
    pass


USER_DOES_NOT_EXIST = _UserDoesNotExist()


@dataclass
class UserDataAdapter:
    storage_adapter: StorageUtility
    _user_data_cache: LRUCache[UserData | _UserDoesNotExist] = field(
        default_factory=lambda: LRUCache[UserData | _UserDoesNotExist](
            ttl=SECONDS_IN_DAY, item_limit=500
        )
    )

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
```

### Single vs double underscore _ for private variables

I had been using double underscores, thinking they were how to used to denote private variables.

```py
class __UserDoesNotExist:
    pass


USER_DOES_NOT_EXIST = __UserDoesNotExist()
```

It turns out that using double underscore triggers name mangling, which causes the error:

`NameError: name '_UserDataAdapter__UserDoesNotExist' is not defined`

The solution is to simply opt for single leading underscore for private variables.

Need to change the rest of the naming convention across the codebase as well.

## Semaphores (and locks)

The semaphores can be done per `chat_id` instead of having a global lock, since each user can only modify their own rows in the first place.

However, doing it in this unbounded way would make it susceptable to memory leaks with an arbitrary amount of users.

A much more manageable way would be to make use of the property that each `chat_id` is an integer (and we pray that the assignment is somewhat random so we have a somewhat normal distribution) and use the last few digits instead to assign a lock to.

Apparently this is known as a striped lock.

```py
@dataclass
class UserDataAdapter:
    _shared_key_locks: list[asyncio.Lock] = field(
        default_factory=lambda: [asyncio.Lock() for _ in range(100)]
    )

    async def add_user(self, chat_id: int):
        "idempotent if the user already exists"
        async with self._shared_key_locks[chat_id % 100]:
            user_data = await self.get_user_data(chat_id)
            if isinstance(user_data, UserData):
                return
            success = await self.storage_adapter.add_user(chat_id)
            if success:
                # update negative cache
                await self.get_user_data(chat_id, True)
```

Also since I'm using a `asyncio.Semaphore` where only 1 coroutine is allowed, this is synonymous to using the `asyncio.Lock`.

Was able to measure between the 2, the memory usage is the same but the creation time is marginally faster for `Lock` over `Semaphore`.

## Mini apps for settings (and search?)

The current way to interact with the app purely through text and buttons is not the most intuitive for functions such as rearranging the list of saved bus stops.

https://github.com/Telegram-Mini-Apps/tma.js
https://docs.telegram-mini-apps.com/platform/init-data#parameters-list

Could experiment with something like passing the list of bus stops to `start_param`, and then receiving the sorted list of stops in the final response for a pure stateless application.

Alternatively we could just have a stateful one by reading off the user's chat_id then retrieving the specific information. However in this case it would also involve the more complex requirement of authenticating actions from a user.

https://docs.telegram-mini-apps.com/platform/init-data#authorization-and-authentication

Also want to point out that the poorest interface right now is the search interface which has to settle for truncating the search results to avoid over cluttering the message.

## Invalid usage

Can have the message handlers throw an incorrect usage error `ErrorIncorrectUsage` when the params are empty.

Applies to:
- search
- route

Also thought about just having a regex to catch when there's no arguments

## Tagging versions on Github

I've added a `github-actions-cd.yml` that triggers when a tagged version is pushed.

Have yet to test it out.

## Classes vs pure DI functions

The initial rewrite of this application involved making use of curried functions to keep track of their own state (separated by responsibility, each maintaining its own context) - which were then composed with other functions to give rise to the complete application state.

This had the tendency to get messy with many layers wrapping around each other.

I've ultimately decided to revert to classes after all, as the most intuitive way of maintaining state within the components.

A small hinderence is how the function types cannot be easily inferred (unlike TypeScript), so we end up having to write a separate type definition to be imported.

```py
type GetNearestStops = Callable[[Coordinate, int], list[BusStop]]
type GetStopInfo = Callable[[str], BusStop | None]
type SearchPossibleStops = Callable[[list[str]], list[BusStop]]


def bus_stop_utility(
    stops: list[BusStop],
) -> tuple[GetNearestStops, GetStopInfo, SearchPossibleStops]:
    def get_nearest_stops(coord: Coordinate, num_stops: int = 3) -> list[BusStop]:
        pass

    def get_stop_info(bus_stop_code: str) -> BusStop | None:
        pass

    def search_possible_stops(query: list[str]) -> list[BusStop]:
        pass

    return (get_nearest_stops, get_stop_info, search_possible_stops)
```

and then a file that uses it will need to import the corresponding type def

```py
from bus_service.bus_stops import GetStopInfo


def _get_reorder_list_message(
    get_stop_info: GetStopInfo, saved_stops: list[str], selected_pos: int
) -> str:
    pass
```

I think that this isn't that bad, considering that it can be treated as a header file of sorts.

## Search feature

The search feature is currently truncated to showing only the first 20 items.

This can be improved to have a paginated query, with callback buttons below to navigate the pages.

The size of the callback_data needs to be 1-64 bytes https://core.telegram.org/bots/api#inlinekeyboardbutton

So we can do something like

`STOPS_HASH`, `page` (starts from 0), `query`

STOPS_HASH can be 8 bytes
page can be be to 3 bytes (current theoretical maximum is 300 pages for 20 results per page for <6000 stops)
2 bytes needed for commas
That leaves 51 bytes for user data, of which we can dedicate 50 bytes for the user and leave 1 byte reserve.

User queries that have length > 50 will be rejected

Since comma `,` needs to be part of the callback data, it should be stripped from the user's query.

Also `transform_query_token` will always give a string that is <= the original, so we can simply return the transformed (and stripped) query within the callback.

Using regex match`r"(\w{8})\,(\d{1,3})\,(.{1,50})"`

### Testing

The test flow for this from telegram should be done manually as well:

1. Queries within and beyond 50 character limit
2. Stale queries after the bus stops list has changed

### Cache enhancement

Can possibly explore caching the search results (e.g. 20 most recent results) as users who have paginated queries are likely to be scrolling through them, so the search results do not need to be regenerated (from the same query via the pagination callback data) each time.

The cache will need to be done within the `BusStopUtility`, via the `search_possible_stops` function.

Should also try to benchmark how long a set of searches might take, to see how much improvement a cache layer might add.

```py
# query: list[str] will need to be converted to a set for immutability to use as a key
_search_stops_result_cache: LRUCache[set[str]] = field(
    default_factory=lambda: LRUCache[set[str]](ttl=0, item_limit=100)
)
# need to remember to clear cache in create method
```

## Updating python version requirements

`.python-version` is currently set to `3.13` (which `uv` takes its configuration from).

Python 3.15 has just been released, so I've been thinking - how do package maintainers usually test that their libraries work with newer versions of python.

Intuitively, this could be checked by running the tests (as well as the application itself) and making sure that it doesn't break, on top of probably running the application itself to make sure that it works.

## Bus stats

A fun thing to build could be bus stats, such as:
- shortest/longest route
- bus stop with most bus services
- bus stops nearest/furthest apart from each other
- most similar bus routes
- bus routes without double or bendy busses (will require repeated sampling)
- most common token
blk 1780
opp 1296
aft 604
bef 485
stn 444
rd 304
exit 255
sch 214
pk 159
ave 154
cp 103
ctr 96
the 88
pr 84
tuas 84
sec 77
b 74
ind 74
2 72
a 69
jln 69
s'pore 67
bt 65
ch 61
1 61
st 57
condo 57
west 57
bldg 56
changi 55
dr 54
int 52
chu 51
kang 51
tampines 50
jurong 49
st. 44
blks 44
east 42
bet 41


## frozenset

https://docs.python.org/3.13/builtins/stdtypes.html#set-types-set-frozenset

Since the frozenset is hashable, it might make sense to just create a set of tuples and obtain its hash, rather than using sha to calculate the hash

However, it turns out the the built-in `hash` function is not stable, and will be different across python sessions and platforms.

Even so, this could still be employed for a future situation where comparisons need to be done within the same session without hashlib hashes.

```py
ls = [1, 2, 3]
# we can store the hashes for future comparison
ls_hash = hash(tuple(ls))

xs = [1, 2, 3]
ys = [1, 2, 3]
# these can be hashed and the hash compared
# assuming a use case where all our lists need to be checked for equality
# this allows us to do n list iterations over k lists and n comparisons O(kn)
# instead of the alternative naive case with n^2 comparisons  by iterating through all elements in the list (n log n by merge comparisons)
```

In contrast, the current implementation also has O(kn) complexity, but with an added overhead cost of the hash function, which is significantly higher (roughly 10x compared to native hash from trivial timeit testing)

## Dataclass

```py
@dataclass(frozen=True, slots=True)
```

An alternative to using a `NamedTuple` would be for a dataclass with frozen and slots.

Slots would prevent additional attributes to be declared after the class instantiation, but is perfect for this use case since we want the data to be immutable anyway (as with frozen to prevent reassignment of attribute values).

There's no reason why slots shouldn't be used except apparently in the case where inheritance needs to happen which 

https://github.com/orgs/community/discussions/168147

When receiving data from the API, we currently use TypedDict to simply type the data for use later on, such that the attribute fields can easily be accessed.
However, this has the unwanted connotation of being mutable after creation.

The alternative would be to either use a NamedTuple or a dataclass(frozen=True, slots=True).

```
Type                 Build (s)   Memory (MiB)   Peak (MiB)    Bytes/row   Access (ms)      ns/row
TypedDict               0.0002           0.95         0.95        192.0         0.748       143.6
NamedTuple              0.0013           0.49         0.49         97.9         0.746       143.1
NamedTupleIdx           0.0013           0.49         0.49         97.9         0.694       133.2
dataclass               0.0012           0.61         0.61        121.9         0.619       118.8
frozen + slots          0.0023           0.41         0.41         81.9         0.616       118.3
```

At 5210 bus stops, the performance gains are quite negligible and network latency will vastly overshadow any performance gains from the different implementations.

Even so, this dataset has given a good and concise context for reasoning about using different data structures and a good reminder **not** to over optimise too early on before a real bottleneck has been identified.

But I still feel that it's a good opportunity to take the switch out implmentations anyway as it's a good opportunity to compare how the different DS are more readable or easier to write, or even how robust the code is to swap things out.
