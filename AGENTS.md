# Counter teaching app

This repository is a minimal deployable teaching example for school students.
All comments, documentation and user-facing text must be in simple English.

- UI: `frontend/app.py`; HTTP API: `backend/main.py`; all SQL: `backend/db.py`.
- Keep the path from button to HTTP request to SQL explicit and small.
- The counter is shared by all visitors, and stored in SQLite, never session state.
- Keep runtime data out of Git. Preserve existing database values on startup.
- Add dependencies with `uv add` or `uv add --dev`, and commit `uv.lock`.
- Before pushing, run `make test` and check the real UI, console and network in a browser.
- Tests include API persistence, concurrent increments and a real browser flow.
- tlfpaas routes `/api*` to the backend and everything else here to the frontend.
- Keep Compose platform-safe: `expose`, no `ports`, no Compose `user`, no external volumes.
- Runtime images must use a non-root Dockerfile `USER` and listen on `0.0.0.0`.
- Keep non-secret deployment defaults in `.docker.env`; secrets belong in the platform UI.
- Read https://deploy.tlfedu.tech/guides/docker/agents.md before changing deployment files.
- Keep short source headers explaining purpose, when to edit, and when to copy.
