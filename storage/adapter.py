import sqlite3

from storage.initialize import init


# TODO use constant for table name
class StorageUtility:
    def __init__(
        self, in_memory: bool | None = None, con: sqlite3.Connection | None = None
    ):
        # TODO: use logging to indicate where the DB is being loaded from
        if in_memory is not None:
            print("serving from mem")
            self.con = sqlite3.connect("file::memory:", uri=True)
            init(self.con)
        elif con is None:
            print("serving from bus_arrival_bot.db")
            self.con = sqlite3.connect("bus_arrival_bot.db")
        else:
            self.con = con
        if not has_init_tables(self.con):
            raise Exception("Database has not been initialized")

    def check_user_exists(self, chat_id: int) -> bool:
        """
        check if a user exists in the database
        """
        try:
            cur = self.con.cursor()
            res = cur.execute(
                """
            SELECT EXISTS(SELECT 1 FROM saved_stops WHERE chat_id = ?);
            """,
                (chat_id,),
            )
            exists: tuple[int] = res.fetchone()
            return exists[0] == 1
        except sqlite3.Error as e:
            # TODO log and handle error
            print(f"SQLite error: {e}")
            return False

    def get_saved_stops(self, chat_id: int) -> list[str]:
        """
        get list of BusStopCode user has saved
        """
        try:
            cur = self.con.cursor()
            res = cur.execute(
                """
            SELECT bus_stop_codes FROM saved_stops WHERE chat_id = ?;
            """,
                (chat_id,),
            )
            saved_stops_res: tuple[str] | None = res.fetchone()
            if saved_stops_res is None or saved_stops_res[0] == "":
                return []
            saved_stops = saved_stops_res[0].split(",")
            return saved_stops
        except sqlite3.Error as e:
            # TODO log and handle error
            print(f"SQLite error: {e}")
            return []

    def save_stops(self, chat_id: int, stops: list[str]) -> bool:
        """
        save list of BusStopCode in DB
        upserts record if chat_id already exists
        """
        saved_stops_str = ",".join(stops)
        try:
            cur = self.con.cursor()
            cur.execute(
                """
            INSERT INTO saved_stops (chat_id, bus_stop_codes) VALUES (?, ?)
            ON CONFLICT(chat_id)
            DO UPDATE SET
            bus_stop_codes = excluded.bus_stop_codes;
            """,
                (chat_id, saved_stops_str),
            )
            self.con.commit()
        except sqlite3.Error as e:
            # TODO handle error
            print(f"SQLite error: {e}")
            return False
        finally:
            return True

    def add_stop(self, chat_id: int, stop_id: str) -> bool:
        """
        add a single bus stop to the saved stops
        """
        saved_stops = self.get_saved_stops(chat_id)
        if stop_id in saved_stops:
            # stop already exists
            return False
        return self.save_stops(chat_id, saved_stops + [stop_id])

    def remove_stop(self, chat_id: int, stop_id: str) -> bool:
        """
        remove a single bus stop from the list of saved stops
        """
        saved_stops = self.get_saved_stops(chat_id)
        for idx, saved_stop_id in enumerate(saved_stops):
            if stop_id == saved_stop_id:
                return self.save_stops(
                    chat_id, saved_stops[:idx] + saved_stops[idx + 1 :]
                )
        return False

    def remove_user(self, chat_id: int) -> bool:
        """
        remove user from DB
        """
        try:
            cur = self.con.cursor()
            cur.execute(
                """
            DELETE FROM saved_stops WHERE chat_id = ?;
            """,
                (chat_id,),
            )
            self.con.commit()
        except sqlite3.Error as e:
            # TODO handle error
            print(f"SQLite error: {e}")
            return False
        finally:
            return True


def has_init_tables(conn: sqlite3.Connection) -> bool:
    """
    Return True if the database contains any user-created tables,
    ignoring SQLite internal tables.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table'
          AND name NOT LIKE 'sqlite_%';
    """)
    return cursor.fetchone() is not None
