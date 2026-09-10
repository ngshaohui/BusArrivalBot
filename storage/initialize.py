import asyncio

import aiosqlite


class StorageUtilityInitError(Exception):
    pass


async def init(con: aiosqlite.Connection):
    try:
        await con.execute("""
        CREATE TABLE users (
            chat_id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL
        );
        """)
        await con.execute("""
        CREATE TABLE saved_stops (
            chat_id INTEGER PRIMARY KEY
                REFERENCES users(chat_id)
                ON DELETE CASCADE,
            bus_stop_codes TEXT NOT NULL
        );
        """)
        await con.execute("""
        CREATE TABLE user_settings (
            chat_id INTEGER PRIMARY KEY
                REFERENCES users(chat_id)
                ON DELETE CASCADE,
            show_load INTEGER NOT NULL DEFAULT 0,
            show_type INTEGER NOT NULL DEFAULT 0
        );
        """)
        await con.commit()
    except aiosqlite.Error as e:
        await con.rollback()
        raise StorageUtilityInitError("Encountered error while initializing DB") from e


async def main():
    con = await aiosqlite.connect("bus_arrival_bot.db")
    await init(con)
    await con.close()


if __name__ == "__main__":
    asyncio.run(main())
