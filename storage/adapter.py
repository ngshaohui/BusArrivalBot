import datetime
import logging

import aiosqlite

from utils.custom_typings import UserSettings

from .initialize import init

logger = logging.getLogger(__name__)


class StorageUtilityTableError(Exception):
    pass


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

    async def check_user_exists(self, chat_id: int) -> bool:
        """
        check if a user exists in the database
        """
        try:
            cur = await self.con.execute(
                """
            SELECT EXISTS(SELECT 1 FROM users WHERE chat_id = ?);
            """,
                (chat_id,),
            )
            # row: tuple[int]
            row = await cur.fetchone()
            return row is not None and row[0] == 1
        except aiosqlite.Error as e:
            # TODO log and handle error
            print(f"SQLite error: {e}")
            return False

    async def add_user(self, chat_id: int) -> bool:
        """
        add a user to the database
        """
        try:
            await self.con.execute(
                "INSERT INTO users (chat_id, created_at) VALUES (?, ?)",
                (chat_id, datetime.datetime.now(datetime.UTC).isoformat()),
            )
            await self.con.execute(
                "INSERT INTO saved_stops (chat_id, bus_stop_codes) VALUES (?, ?)",
                (chat_id, ""),
            )
            await self.con.execute(
                "INSERT INTO user_settings (chat_id) VALUES (?)",
                (chat_id,),
            )
            await self.con.commit()
            return True
        except aiosqlite.Error as e:
            await self.con.rollback()
            # TODO log and handle error
            print(f"SQLite error: {e}")
            return False

    async def get_saved_stops(self, chat_id: int) -> list[str] | None:
        """
        get list of BusStopCode user has saved
        """
        try:
            cur = await self.con.execute(
                """
            SELECT bus_stop_codes FROM saved_stops WHERE chat_id = ?;
            """,
                (chat_id,),
            )
            # row: tuple[str] | None
            row = await cur.fetchone()
            if row is None:
                return None
            elif row[0] == "":
                return []
            saved_stops = row[0].split(",")
            return saved_stops
        except aiosqlite.Error as e:
            # TODO log and handle error
            print(f"SQLite error: {e}")
            return None

    async def save_stops(self, chat_id: int, stops: list[str]) -> bool:
        """
        save list of BusStopCode in DB
        upserts record if chat_id already exists
        """
        saved_stops_str = ",".join(stops)
        try:
            await self.con.execute(
                """
            INSERT INTO saved_stops (chat_id, bus_stop_codes) VALUES (?, ?)
            ON CONFLICT(chat_id)
            DO UPDATE SET
            bus_stop_codes = excluded.bus_stop_codes;
            """,
                (chat_id, saved_stops_str),
            )
            await self.con.commit()
            return True
        except aiosqlite.Error as e:
            # TODO handle error
            print(f"SQLite error: {e}")
            return False

    async def save_user_settings(
        self, chat_id: int, show_load: int, show_type: int
    ) -> bool:
        try:
            await self.con.execute(
                """
                INSERT INTO user_settings (chat_id, show_load, show_type)
                VALUES (?, ?, ?)
                ON CONFLICT(chat_id)
                DO UPDATE SET
                    show_load = excluded.show_load,
                    show_type = excluded.show_type;
                """,
                (chat_id, show_load, show_type),
            )
            await self.con.commit()
            return True
        except aiosqlite.Error as e:
            # TODO handle error
            print(f"SQLite error: {e}")
            return False

    async def get_user_settings(self, chat_id: int) -> UserSettings | None:
        try:
            cur = await self.con.execute(
                """
            SELECT show_load, show_type FROM user_settings WHERE chat_id = ?
            """,
                (chat_id,),
            )
            # row will be tuple[int, int] | None but aiosqlite typing doesn't allow trivial casting
            row = await cur.fetchone()
            if row is None:
                return None
            return UserSettings(bool(row[0]), bool(row[1]))
        except aiosqlite.Error as e:
            # TODO log and handle error
            print(f"SQLite error: {e}")
            return None

    async def remove_user(self, chat_id: int) -> bool:
        """
        remove user from DB
        """
        try:
            await self.con.execute(
                """
            DELETE FROM users WHERE chat_id = ?;
            """,
                (chat_id,),
            )
            await self.con.commit()
            return True
        except aiosqlite.Error as e:
            # TODO handle error
            print(f"SQLite error: {e}")
            return False


async def raise_if_table_not_init(conn: aiosqlite.Connection):
    """
    Check if required tables are present
    """
    cur = await conn.execute("""
        SELECT COUNT(*) 
        FROM sqlite_master 
        WHERE type='table'
          AND name IN ('users', 'saved_stops', 'user_settings');
    """)
    row = await cur.fetchone()
    if row is None or row[0] != 3:
        raise StorageUtilityTableError("Table(s) not initialized in DB")
