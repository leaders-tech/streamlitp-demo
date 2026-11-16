# Streamlit + API + SQLite

A minimal deployable teaching example for IB DP Computer Science students.
Click **Add 1** to increase a shared counter. Reload the page or restart the API:
the value stays in SQLite. All visitors use the same counter. An open page shows
the last value it loaded; reload to see another visitor's changes.

## How a click works

1. The browser sends the button event to the Streamlit Python server.
2. The Python UI sends `POST /api/counter/increment` to the FastAPI server.
3. The API runs an atomic SQL update and returns `{"value": 1}`.
4. The UI displays the returned value.

The UI never opens the database. These Python UI frameworks use a WebSocket
between browser and UI server, so the API call appears in the Python server,
not as a browser fetch request. Ordinary page loads use `GET /api/counter`.

## Run locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.14.
From the repository root:

```sh
make install
```

Open two terminals in this folder:

```sh
# Terminal 1: API on port 8081
make backend
```

```sh
# Terminal 2: UI on port 8080
make frontend
```

Open http://localhost:8080. Local SQLite data lives in `data/counter.sqlite3`
(ignored by Git). Stop each server with Ctrl+C.

## Files to read and change

| File | Purpose |
| --- | --- |
| `frontend/app.py` | Page, button and HTTP requests |
| `backend/main.py` | API routes and startup |
| `backend/db.py` | SQLite table and SQL queries |
| `tests/test_api.py` | Persistence and concurrent request tests |
| `tests/test_browser.py` | Real browser clicks, reloads and API error handling |
| `docker-compose.yml` | UI, API and persistent database volume |
| `.docker.env` | Non-secret deployment defaults |
| `Dockerfile` | Non-root runtime with locked dependencies |

## Try the API

```sh
curl http://localhost:8081/api/counter
curl -X POST http://localhost:8081/api/counter/increment
curl http://localhost:8081/api/health
```

Interactive API documentation: http://localhost:8081/api/docs.
GET only reads. POST increments. No request body is needed.

## Test before pushing

```sh
make test
```

The suite starts temporary servers on unused ports, uses a temporary database,
and opens headless Chromium. It does not change your local counter. Run
`uv run playwright install --with-deps chromium` on Linux if browser libraries
are missing. For a manual check, open the app, click, reload, and check the browser
console and network for errors.

## Deploy on tlfpaas

1. Push this repository to GitHub and connect it to your tlfpaas project.
2. The platform reads `docker-compose.yml`, builds both services and publishes
   the project URL. See the latest deploy log on the project dashboard.
3. Open the public URL and click **Add 1**. No secrets are needed for this example.

The frontend listens on `0.0.0.0:8080`; the API listens on `0.0.0.0:8081`.
The platform sends `/api*` to the API and the UI's pages and WebSocket traffic
to the frontend. `API_URL=http://backend:8081` uses Docker's private service name.
Both services use the same Dockerfile; the backend overrides the start command.
Compose deliberately uses `expose`, without publishing host ports.

The `counter_data` named volume is mounted at `/data` in the API service.
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
