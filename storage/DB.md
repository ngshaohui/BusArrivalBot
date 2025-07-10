# Database

The database shall be used to store user settings.

## Schema

### saved_stops

| column                | type    | constraints | purpose         |
| --------------------- | ------- | ----------- | --------------- |
| chat_id (PRIMARY KEY) | INTEGER | NOT NULL    | chat_id of user |
| bus_stop_codes        | TEXT    | NOT NULL    | bus stop codes  |

### Table: `saved_stops`

The column `busses` shall be a comma separated list of service numbers.

## Init commands

```sql
CREATE TABLE saved_stops (
    chat_id INTEGER PRIMARY KEY,
    bus_stop_codes TEXT NOT NULL
);

CREATE TABLE stop_settings (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    bus_stop_code TEXT NOT NULL,
    busses TEXT NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES saved_stops (chat_id) ON DELETE CASCADE,
    UNIQUE (chat_id, bus_stop_code)
);

CREATE INDEX idx_chat_id ON stop_settings (chat_id);
```

## ORM

Consider using an ORM to interface with the DB instead of using raw SQL queries.
