# Streamlit + SQLite

A minimal deployable teaching example for IB DP Computer Science students.
Click **Add 1** to increase a shared counter. Reload the page or restart the app:
the value stays in SQLite. All visitors use the same counter, and every open page
shows a new value within two seconds, without a reload.

## How a click works

1. The browser sends the button event to the Streamlit Python server over its WebSocket.
2. Streamlit reruns `main.py`. This time `st.button("Add 1")` returns `True`,
   so the script calls `db.increment()`.
3. `db.increment()` runs one atomic SQL update.
4. The rest of the script runs and shows the new count.

Other open pages run the small `show_count` fragment every two seconds. It reads
the count again, so they see your click without a reload. There is no HTTP request
between the page and the database: the script is ordinary Python on the server,
so it calls your code directly.

## Run locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.14.
From the repository root:

```sh
make install
make run
```

Open http://localhost:8080. Open it in a second tab too and click there.
Local SQLite data lives in `data/counter.sqlite3` (ignored by Git).
Stop the server with Ctrl+C.

## Files to read and change

| File | Purpose |
| --- | --- |
| `main.py` | The page: button and count |
| `server.py` | Starts the page and the HTTP routes in one process |
| `db.py` | SQLite table and SQL queries |
| `tests/test_db.py` | Persistence and concurrent click tests |
| `tests/test_browser.py` | Real browser clicks, live updates, API and restart |
| `docker-compose.yml` | One service and the persistent database volume |
| `.docker.env` | Non-secret deployment defaults |
| `Dockerfile` | Non-root runtime with locked dependencies |

## Try the API

`server.py` wraps the page in `st.App` (Streamlit 1.67 and later) and adds three
HTTP routes next to it, in the same process. `streamlit run server.py` finds the
`app` and serves both. The page does not need the routes; they are for other
programs, such as `curl` or a script:

```sh
curl http://localhost:8080/api/counter
curl -X POST http://localhost:8080/api/counter/increment
curl http://localhost:8080/api/health
```

GET only reads. POST increments, and open pages show it within two seconds.
If you don't need an API, delete `server.py` and run `streamlit run main.py`,
after moving its `db.initialize()` call to the top of `main.py`.

## Test before pushing

```sh
make test
```

The suite starts a temporary server on an unused port, uses a temporary database,
and opens headless Chromium. It does not change your local counter. Run
`uv run playwright install --with-deps chromium` on Linux if browser libraries
are missing. For a manual check, open the app in two tabs, click, reload, and check
the browser console and network for errors.

## Deploy on tlfpaas

1. Push this repository to GitHub and connect it to your tlfpaas project.
2. The platform reads `docker-compose.yml`, builds the `web` service and publishes
   the project URL. See the latest deploy log on the project dashboard.
3. Open the public URL and click **Add 1**. No secrets are needed for this example.

The app listens on `0.0.0.0:8080`, and the `tlfpaas.route: "web"` label sends all
traffic there: pages, the WebSocket and `/api`. Compose deliberately uses `expose`,
without publishing host ports.

The `counter_data` named volume is mounted at `/data`.
`DB_PATH=/data/counter.sqlite3` keeps the database across restarts and redeploys.
Keep that path inside `/data`. Deleting the volume deletes the counter.

Non-secret defaults live in `.docker.env` and are declared in `x-tlfpaas`.
To change them, use the project's **Settings** page and then **Redeploy now**.
If you later add passwords or API keys, put them in **Secrets**, never in Git,
and redeploy. This counter has no login: everyone with the URL can increment it.

- [Deploys](https://deploy.tlfedu.tech/guides/students/deploys.md)
- [Settings](https://deploy.tlfedu.tech/guides/students/settings.md)
- [Secrets](https://deploy.tlfedu.tech/guides/students/secrets.md)
- [Student Docker guide](https://deploy.tlfedu.tech/guides/docker/students.md)
- [Agent Docker contract](https://deploy.tlfedu.tech/guides/docker/agents.md)
