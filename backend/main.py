"""Expose the counter HTTP API. Edit routes here; copy a route for a new endpoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.initialize()
    yield


# Keep API docs under /api so they also work through the deployment proxy.
app = FastAPI(
    title="Counter API", lifespan=lifespan,
    docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None,
)


@app.get("/api/health")
def health() -> dict[str, str]:
    db.read()  # Report healthy only if the database can also be read.
    return {"status": "ok"}


@app.get("/api/counter")
def read_counter() -> dict[str, int]:
    return {"value": db.read()}


@app.post("/api/counter/increment")
def increment_counter() -> dict[str, int]:
    return {"value": db.increment()}
