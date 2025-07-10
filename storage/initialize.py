import sqlite3

TABLE_NAME = "saved_stops"


def init(con: sqlite3.Connection):
    try:
        cur = con.cursor()
        cur.execute(f"""
        CREATE TABLE {TABLE_NAME} (
            chat_id INTEGER PRIMARY KEY,
            bus_stop_codes TEXT NOT NULL
        );
        """)
        con.commit()
    except sqlite3.Error as e:
        raise Exception("Encountered error while initializing DB", e)


def main():
    con = sqlite3.connect("bus_arrival_bot.db")
    init(con)
    con.close()


def populate_dummy():
    con = sqlite3.connect("bus_arrival_bot.db")
    try:
        cur = con.cursor()
        save_stops = [
            (127038678, "45029,43099,42071")
        ]
        cur.executemany("""
        INSERT INTO saved_stops (chat_id, bus_stop_codes) VALUES(?, ?)
        """, save_stops)
        con.commit()
    except sqlite3.Error as e:
        raise Exception("Encountered error while populating DB", e)
    finally:
        con.close()


if __name__ == "__main__":
    main()
    populate_dummy()
