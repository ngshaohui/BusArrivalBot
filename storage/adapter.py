import sqlite3
from typing import Callable

type GetSavedStops = Callable[[int], list[str]]
type SaveStops = Callable[[int, list[str]], bool]


class StorageUtility:
    def __init__(self, con: sqlite3.Connection | None = None):
        if con is None:
            self.con = sqlite3.connect("bus_arrival_bot.db")
        else:
            self.con = con

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
            if saved_stops_res is None:
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
        uperts record if chat_id already exists
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
