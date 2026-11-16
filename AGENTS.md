# Counter teaching app

This repository is a minimal deployable teaching example for school students.
All comments, documentation and user-facing text must be in simple English.

- One process: `main.py` is the page, `server.py` adds HTTP routes with `st.App`,
  and all SQL is in `db.py`.
- Use Streamlit the standard way: the script calls Python code directly when a
  button is clicked. Extra HTTP routes go in `server.py`, never in a second server.
- The counter is shared by all visitors, and stored in SQLite, never session state.
  A `st.fragment` with `run_every` shows other visitors' clicks without reloads.
- Keep runtime data out of Git. Preserve existing database values on startup.
- Add dependencies with `uv add` or `uv add --dev`, and commit `uv.lock`.
- Before pushing, run `make test` and check the real UI, console and network in a browser.
- Tests include SQLite persistence, concurrent increments and a real browser flow.
- Keep Compose platform-safe: `expose`, no `ports`, no Compose `user`, no external volumes.
- Runtime images must use a non-root Dockerfile `USER` and listen on `0.0.0.0`.
- Keep non-secret deployment defaults in `.docker.env`; secrets belong in the platform UI.
- Read https://deploy.tlfedu.tech/guides/docker/agents.md before changing deployment files.
- Keep short source headers explaining purpose, when to edit, and when to copy.
