"""Check real UI clicks and API failures. Edit for UI changes; copy for another page."""

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
def server(command, env, ready_url, log_path):
    # Files preserve useful server output if a browser test fails.
    with log_path.open("a") as log:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=log)
        try:
            wait_until_ready(ready_url, process)
            yield process
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def test_click_reload_restart_and_api_error(tmp_path):
    api_port, ui_port = unused_port(), unused_port()
    api_url = f"http://127.0.0.1:{api_port}"
    ui_url = f"http://127.0.0.1:{ui_port}"
    env = dict(os.environ, DB_PATH=str(tmp_path / "counter.sqlite3"),
               API_URL=api_url, PORT=str(ui_port))
    # Child servers are normal applications, not NiceGUI pytest screen fixtures.
    env.pop("PYTEST_CURRENT_TEST", None)
    api_command = [sys.executable, "-m", "uvicorn", "backend.main:app",
                   "--host", "127.0.0.1", "--port", str(api_port)]
    ui_command = [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.address=127.0.0.1", f"--server.port={ui_port}", "--server.headless=true", "--browser.gatherUsageStats=false"]
    with server(api_command, env, f"{api_url}/api/health", tmp_path / "api.log") as api:
        with server(ui_command, env, f"{ui_url}/_stcore/health", tmp_path / "ui.log"):
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page()
                errors, failed_requests = [], []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("console", lambda message: errors.append(message.text)
                        if message.type == "error" else None)
                page.on("requestfailed", lambda request: failed_requests.append(request.url))
                page.goto(ui_url)
                expect(page.get_by_text("Count: 0", exact=True)).to_be_visible()
                page.get_by_role("button", name="Add 1", exact=True).click()
                expect(page.get_by_text("Count: 1", exact=True)).to_be_visible()
                assert httpx.get(f"{api_url}/api/counter").json() == {"value": 1}
                page.reload()
                expect(page.get_by_text("Count: 1", exact=True)).to_be_visible()
                # A new browser session must read the same shared database.
                other = browser.new_page()
                other.goto(ui_url)
                expect(other.get_by_text("Count: 1", exact=True)).to_be_visible()
                other.get_by_role("button", name="Add 1", exact=True).click()
                expect(other.get_by_text("Count: 2", exact=True)).to_be_visible()
                other.close()
                # Stop the API while leaving the UI up: show a friendly error.
                api.terminate()
                api.wait(timeout=10)
                page.get_by_role("button", name="Add 1", exact=True).click()
                expect(page.get_by_text("Cannot reach the API. Please try again.", exact=True)).to_be_visible()
                with server(api_command, env, f"{api_url}/api/health", tmp_path / "api.log"):
                    page.reload()
                    expect(page.get_by_text("Count: 2", exact=True)).to_be_visible()
                    page.get_by_role("button", name="Add 1", exact=True).click()
                    expect(page.get_by_text("Count: 3", exact=True)).to_be_visible()
                assert errors == []
                assert failed_requests == []
                browser.close()
