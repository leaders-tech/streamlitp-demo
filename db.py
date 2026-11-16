"""Store the shared counter in SQLite. Edit SQL here; copy for another small table."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path


def connect() -> sqlite3.Connection:
    # /data is a persistent Docker volume; local runs use the ignored data folder.
    path = Path(os.environ.get("DB_PATH", "data/counter.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path, timeout=10)


def initialize() -> None:
    with closing(connect()) as connection, connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS counter "
            "(id INTEGER PRIMARY KEY CHECK (id = 1), value INTEGER NOT NULL)"
        )
        # Starting the server again must not reset an existing counter.
        connection.execute("INSERT OR IGNORE INTO counter (id, value) VALUES (1, 0)")


def read() -> int:
    with closing(connect()) as connection:
        return connection.execute("SELECT value FROM counter WHERE id = 1").fetchone()[0]


def increment() -> int:
    with closing(connect()) as connection, connection:
        # One SQL update avoids losing clicks when several users click together.
        return connection.execute(
            "UPDATE counter SET value = value + 1 WHERE id = 1 RETURNING value"
        ).fetchone()[0]
