# Common student commands. Edit when commands change; copy for a small Python app.
.PHONY: install backend frontend test
install:
	uv sync --locked
	uv run playwright install chromium

backend:
	uv run uvicorn backend.main:app --host 0.0.0.0 --port 8081

frontend:
	uv run streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=8080 --server.headless=true --browser.gatherUsageStats=false

test:
	uv run pytest -q
