import sqlite3
from typing import Callable

type GetSavedStops = Callable[[int], list[str]]
type SaveStops = Callable[[int, list[str]], bool]


def storage_utility() -> tuple[GetSavedStops, SaveStops]:
    """
    TODO describe
    """
    con = sqlite3.connect("bus_arrival_bot.db")
    return storage_utility_h(con)


def storage_utility_h(con: sqlite3.Connection) -> tuple[GetSavedStops, SaveStops]:
    def get_saved_stops(chat_id: int) -> list[str]:
        """
        get list of BusStopCode user has saved
        """
        try:
            cur = con.cursor()
            res = cur.execute("""
            SELECT bus_stop_codes FROM saved_stops WHERE chat_id = ?;
            """, (chat_id,))
            saved_stops_res: tuple[str] | None = res.fetchone()
            if saved_stops_res is None:
                return []
            saved_stops = saved_stops_res[0].split(",")
            return saved_stops
        except sqlite3.Error as e:
            # TODO log and handle error
            print(f"SQLite error: {e}")
            return []

    def save_stops(chat_id: int, stops: list[str]) -> bool:
        """
        save list of BusStopCode in DB
        uperts record if chat_id already exists
        """
        saved_stops_str = ",".join(stops)
        try:
            cur = con.cursor()
            cur.execute("""
            INSERT INTO saved_stops (chat_id, bus_stop_codes) VALUES (?, ?)
            ON CONFLICT(chat_id)
            DO UPDATE SET
            bus_stop_codes = excluded.bus_stop_codes;
            """, (chat_id, saved_stops_str))
            con.commit()
        except sqlite3.Error as e:
            # TODO handle error
            print(f"SQLite error: {e}")
            return False
        finally:
            return True

    return get_saved_stops, save_stops
