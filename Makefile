# Common student commands. Edit when commands change; copy for a small Python app.
.PHONY: install run test
install:
	uv sync --locked
	uv run playwright install chromium

run:
	uv run streamlit run server.py --server.address=0.0.0.0 --server.port=8080 --server.headless=true --browser.gatherUsageStats=false

test:
	uv run pytest -q
