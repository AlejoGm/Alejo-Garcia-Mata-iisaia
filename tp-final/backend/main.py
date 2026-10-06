import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from backend import config
from sqlmodel import Session

from backend.catalog import seed_exercises
from backend.db import create_tables, engine
from backend.routes import campaigns, duels, exercises, groups, me, rankings, routines, sessions

FRONTEND_DIR = config.ROOT / "frontend"

log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_tables()
    with Session(engine) as session:
        seed_exercises(session)
    if config.AUTH_MODE == "dev":
        log.warning("Auth0 no está configurado: login de desarrollo, sin Google. Ver README.")
    yield


app = FastAPI(title="Gym-bro", lifespan=lifespan)


@app.middleware("http")
async def revalidate_static(request: Request, call_next):
    # Sin build no hay hashes en los nombres: que el navegador revalide siempre los módulos.
    response = await call_next(request)
    if not request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-cache"
    return response

# Los routers van antes del montaje en "/", que atrapa todo lo que llega después.
for module in (me, exercises, groups, sessions, rankings, routines, duels, campaigns):
    app.include_router(module.router)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
