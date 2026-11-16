"""Start the Streamlit page and its small HTTP API in one process. Edit routes here."""

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

import streamlit as st

import db


# The page in main.py does not use these routes; it calls db.py directly.
# They are only for other programs, such as curl or a script.
async def health(request: Request) -> JSONResponse:
    db.read()  # Report healthy only if the database can also be read.
    return JSONResponse({"status": "ok"})


async def read_counter(request: Request) -> JSONResponse:
    return JSONResponse({"value": db.read()})


async def increment_counter(request: Request) -> JSONResponse:
    return JSONResponse({"value": db.increment()})


db.initialize()

# `streamlit run server.py` finds this `app` and serves main.py next to the routes.
app = st.App("main.py", routes=[
    Route("/api/health", health, methods=["GET"]),
    Route("/api/counter", read_counter, methods=["GET"]),
    Route("/api/counter/increment", increment_counter, methods=["POST"]),
])
