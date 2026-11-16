"""Check the SQLite counter. Edit for SQL changes; copy for another small table."""

from concurrent.futures import ThreadPoolExecutor

import pytest

import db


@pytest.fixture(autouse=True)
def temporary_database(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "counter.sqlite3"))
    db.initialize()


def test_read_and_increment():
    assert db.read() == 0
    assert db.increment() == 1
    assert db.read() == 1


def test_counter_survives_restart():
    db.increment()
    # Starting the server again runs initialize again on the same file.
    db.initialize()
    assert db.read() == 1


def test_simultaneous_clicks_are_not_lost():
    with ThreadPoolExecutor(max_workers=8) as pool:
        values = list(pool.map(lambda _: db.increment(), range(30)))
    assert sorted(values) == list(range(1, 31))
    assert db.read() == 30
