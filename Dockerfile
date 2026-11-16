# Build a locked Python runtime. Edit for system packages; copy for a similar app.
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY server.py main.py db.py ./
# The volume inherits this ownership when Docker creates it for the first time.
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --create-home app \
    && mkdir /data && chown app:app /data
USER app
EXPOSE 8080
CMD [".venv/bin/streamlit", "run", "server.py", "--server.address=0.0.0.0", "--server.port=8080", "--server.headless=true", "--browser.gatherUsageStats=false"]
