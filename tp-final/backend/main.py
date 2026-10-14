import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from sqlalchemy.exc import OperationalError
from fastapi.staticfiles import StaticFiles

from backend import config
from sqlmodel import Session

from backend.catalog import seed_exercises
from backend.db import create_tables, engine
from backend.routes import (
    accounts, bro, campaigns, compare, dashboard, duels, exercises, groups, me, me_stats, rankings, routines, sessions, standing,
)

FRONTEND_DIR = config.ROOT / "frontend"

log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_tables()
    try:
        with Session(engine) as session:
            seed_exercises(session)
    except OperationalError as err:
        # create_all no modifica tablas existentes: una base de una versión anterior queda incompatible.
        raise RuntimeError(f"La base {config.DB_PATH} es de una versión anterior de la app. "
                           "Renombrala o borrala y volvé a arrancar.") from err
    if config.AUTH_MODE == "dev":
        log.warning("Login de desarrollo: se entra solo con un nombre, sin contraseña. No usar fuera de esta máquina.")
    elif config.AUTH_MODE == "local":
        log.info("Login con usuario y contraseña. Para entrar con Google, configurar Auth0 (ver README).")
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
for module in (accounts, me, exercises, groups, sessions, rankings, routines, duels, campaigns, me_stats, dashboard, bro, standing, compare):
    app.include_router(module.router)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
