import asyncio

import aiosqlite


class StorageUtilityInitError(Exception):
    pass


async def apply(con: aiosqlite.Connection):
    try:
        await con.execute("""
        ALTER TABLE user_settings
        ADD show_sequence INTEGER NOT NULL DEFAULT 0
        """)
        await con.commit()
    except aiosqlite.Error as e:
        await con.rollback()
        raise StorageUtilityInitError("Encountered error during migration") from e


async def rollback(con: aiosqlite.Connection):
    try:
        await con.execute("""
        ALTER TABLE user_settings
        DROP COLUMN show_sequence
        """)
        await con.commit()
    except aiosqlite.Error as e:
        await con.rollback()
        raise StorageUtilityInitError("Encountered error during rollback") from e


async def main():
    con = await aiosqlite.connect("bus_arrival_bot.db")
    await apply(con)
    await con.close()


if __name__ == "__main__":
    asyncio.run(main())
