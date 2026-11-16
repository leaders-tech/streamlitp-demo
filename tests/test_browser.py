"""Check real UI clicks, live updates and the API. Edit for UI changes; copy for another page."""

import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import httpx
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def unused_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def wait_until_ready(url, process):
    for _ in range(150):
        if process.poll() is not None:
            raise AssertionError("The test server stopped before it was ready.")
        try:
            if httpx.get(url, timeout=1).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.1)
    raise AssertionError(f"The test server did not become ready: {url}")


@contextmanager
def server(env, url, log_path):
    # A file keeps the server output if a browser test fails.
    with log_path.open("a") as log:
        command = [sys.executable, "-m", "streamlit", "run", "server.py",
                   "--server.address=127.0.0.1", f"--server.port={url.rsplit(':', 1)[1]}",
                   "--server.headless=true", "--browser.gatherUsageStats=false"]
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=log)
        try:
            wait_until_ready(f"{url}/api/health", process)
            yield process
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def test_click_live_update_api_and_restart(tmp_path):
    port = unused_port()
    url = f"http://127.0.0.1:{port}"
    env = dict(os.environ, DB_PATH=str(tmp_path / "counter.sqlite3"))
    log = tmp_path / "server.log"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        errors, failed_requests = [], []

        def open_page():
            page = browser.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda message: errors.append(message.text)
                    if message.type == "error" else None)
            page.on("requestfailed", lambda request: failed_requests.append(request.url))
            page.goto(url)
            return page

        with server(env, url, log):
            page = open_page()
            expect(page.get_by_text("Count: 0", exact=True)).to_be_visible()
            page.get_by_role("button", name="Add 1", exact=True).click()
            expect(page.get_by_text("Count: 1", exact=True)).to_be_visible()
            assert httpx.get(f"{url}/api/counter").json() == {"value": 1}

            # A click in another tab shows up here within two seconds, without a reload.
            other = open_page()
            expect(other.get_by_text("Count: 1", exact=True)).to_be_visible()
            other.get_by_role("button", name="Add 1", exact=True).click()
            expect(page.get_by_text("Count: 2", exact=True)).to_be_visible()

            # So does an increment through the HTTP API.
            assert httpx.post(f"{url}/api/counter/increment").json() == {"value": 3}
            expect(page.get_by_text("Count: 3", exact=True)).to_be_visible()
            # A GET must never change state, even if someone opens the increment URL.
            httpx.get(f"{url}/api/counter/increment")
            assert httpx.get(f"{url}/api/counter").json() == {"value": 3}
            other.close()
            page.close()

        # A fresh server reads the same SQLite file.
        with server(env, url, log):
            page = open_page()
            expect(page.get_by_text("Count: 3", exact=True)).to_be_visible()
            page.get_by_role("button", name="Add 1", exact=True).click()
            expect(page.get_by_text("Count: 4", exact=True)).to_be_visible()
            page.close()

        browser.close()
    assert errors == []
    assert failed_requests == []
