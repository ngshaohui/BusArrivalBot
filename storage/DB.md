# Database

The database shall be used to store user settings.

## Schema

### Table: `users`

| column                | type    | constraints | purpose         |
| --------------------- | ------- | ----------- | ----------------|
| chat_id (PK)          | INTEGER | NOT NULL    | chat_id of user |
| created_at            | TEXT    | NOT NULL    | creation date   |

Subsequent tables will have `chat_id` column as a FK and set to `ON DELETE CASCADE`.

### Table: `saved_stops`

| column                | type    | constraints | purpose         |
| --------------------- | ------- | ----------- | --------------- |
| chat_id (PK, FK)      | INTEGER | NOT NULL    | chat_id of user |
| bus_stop_codes        | TEXT    | NOT NULL    | bus stop codes  |

The column `bus_stop_codes` shall be a comma separated list of service numbers.

This has the added benefit of denoting the order the list is to be shown to the user.

### Table: `user_settings`

| column                | type    | constraints          | purpose         |
| --------------------- | ------- | -------------------- | --------------- |
| chat_id (PK, FK)      | INTEGER | NOT NULL             | chat_id of user |
| show_load             | INTEGER | NOT NULL DEFAULT 0   | show bus load   |
| show_type             | INTEGER | NOT NULL DEFAULT 0   | show bus load   |

The columns `show_load` and `show_type` shall be an integer 0 (false, default) or 1 (true).

## Init commands

```sql
CREATE TABLE users (
    chat_id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL
);

CREATE TABLE saved_stops (
    chat_id INTEGER PRIMARY KEY
        REFERENCES users(chat_id)
        ON DELETE CASCADE,
    bus_stop_codes TEXT NOT NULL
);


CREATE TABLE user_settings (
    chat_id INTEGER PRIMARY KEY
        REFERENCES users(chat_id)
        ON DELETE CASCADE,
    show_load INTEGER NOT NULL DEFAULT 0,
    show_type INTEGER NOT NULL DEFAULT 0
);

-- future implementation, not present
CREATE TABLE stop_settings (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    bus_stop_code TEXT NOT NULL,
    busses TEXT NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES saved_stops (chat_id) ON DELETE CASCADE,
    UNIQUE (chat_id, bus_stop_code)
);
```

## Foreign key enforcement

FK enforcement is turned off by default, need to explicitly enable it.

```py
conn = sqlite3.connect("app.db")
conn.execute("PRAGMA foreign_keys = ON")
```

## ORM

Consider using an ORM to interface with the DB instead of using raw SQL queries.
