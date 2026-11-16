"""Check HTTP and SQLite behavior. Edit for API changes; copy for a new endpoint."""

from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "counter.sqlite3"))
    with TestClient(app) as client:
        yield client


def test_read_increment_and_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/counter").json() == {"value": 0}
    response = client.post("/api/counter/increment")
    assert response.status_code == 200
    assert response.json() == {"value": 1}
    assert client.get("/api/counter").json() == {"value": 1}
    # A GET must never change state, even if someone opens the increment URL.
    assert client.get("/api/counter/increment").status_code == 405
    assert client.get("/api/counter").json() == {"value": 1}


def test_counter_survives_api_restart(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "counter.sqlite3"))
    with TestClient(app) as first:
        first.post("/api/counter/increment")
    # Entering the lifespan again simulates a fresh server using the same file.
    with TestClient(app) as restarted:
        assert restarted.get("/api/counter").json() == {"value": 1}


def test_simultaneous_clicks_are_not_lost(client):
    def click(_):
        response = client.post("/api/counter/increment")
        assert response.status_code == 200
        return response.json()["value"]

    with ThreadPoolExecutor(max_workers=8) as pool:
        values = list(pool.map(click, range(30)))
    assert sorted(values) == list(range(1, 31))
    assert client.get("/api/counter").json() == {"value": 30}
