import datetime
import sqlite3


class DBMigrationError(Exception):
    pass


def main():
    cur_timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    conn = sqlite3.connect("bus_arrival_bot.db")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        # save data to memory first
        res = conn.execute("""
            SELECT chat_id, bus_stop_codes FROM saved_stops
        """)
        saved_stops_res: list[tuple[int, str]] = res.fetchall()

        # delete rows from table
        conn.execute("DROP TABLE saved_stops")

        # recreate tables
        conn.execute("""
        CREATE TABLE users (
            chat_id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL
        );
        """)
        conn.execute("""
        CREATE TABLE saved_stops (
            chat_id INTEGER PRIMARY KEY
                REFERENCES users(chat_id)
                ON DELETE CASCADE,
            bus_stop_codes TEXT NOT NULL
        );
        """)
        conn.execute("""
        CREATE TABLE user_settings (
            chat_id INTEGER PRIMARY KEY
                REFERENCES users(chat_id)
                ON DELETE CASCADE,
            show_load INTEGER NOT NULL DEFAULT 0,
            show_type INTEGER NOT NULL DEFAULT 0
        );
        """)

        # add rows back to tables
        # - users
        conn.executemany(
            """
        INSERT INTO users (chat_id, created_at) VALUES(?, ?)
        """,
            [(row[0], cur_timestamp) for row in saved_stops_res],
        )

        # - saved_stops
        conn.executemany(
            """
        INSERT INTO saved_stops (chat_id, bus_stop_codes) VALUES(?, ?)
        """,
            saved_stops_res,
        )

        # - user_settings
        conn.executemany(
            """
        INSERT INTO user_settings (chat_id) VALUES(?)
        """,
            [(row[0],) for row in saved_stops_res],
        )

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise DBMigrationError("Encountered error while migrating DB") from e
    finally:
        conn.close()
        print("migration complete")


if __name__ == "__main__":
    main()
