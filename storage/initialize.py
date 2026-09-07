import sqlite3


class StorageUtilityInitError(Exception):
    pass


def init(con: sqlite3.Connection):
    try:
        con.execute("""
        CREATE TABLE users (
            chat_id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL
        );
        """)
        con.execute("""
        CREATE TABLE saved_stops (
            chat_id INTEGER PRIMARY KEY
                REFERENCES users(chat_id)
                ON DELETE CASCADE,
            bus_stop_codes TEXT NOT NULL
        );
        """)
        con.execute("""
        CREATE TABLE user_settings (
            chat_id INTEGER PRIMARY KEY
                REFERENCES users(chat_id)
                ON DELETE CASCADE,
            show_load INTEGER NOT NULL DEFAULT 0,
            show_type INTEGER NOT NULL DEFAULT 0
        );
        """)
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        raise StorageUtilityInitError("Encountered error while initializing DB") from e


def main():
    con = sqlite3.connect("bus_arrival_bot.db")
    init(con)
    con.close()


def populate_dummy():
    con = sqlite3.connect("bus_arrival_bot.db")
    try:
        cur = con.cursor()
        save_stops = [(127038678, "45029,43099,42071")]
        cur.executemany(
            """
        INSERT INTO saved_stops (chat_id, bus_stop_codes) VALUES(?, ?)
        """,
            save_stops,
        )
        con.commit()
    except sqlite3.Error as e:
        raise StorageUtilityInitError("Encountered error while populating DB", e)
    finally:
        con.close()


if __name__ == "__main__":
    main()
