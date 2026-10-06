import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend import config
from backend.db import create_tables
from backend.routes import me

FRONTEND_DIR = config.ROOT / "frontend"

log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_tables()
    if config.AUTH_MODE == "dev":
        log.warning("Auth0 no está configurado: login de desarrollo, sin Google. Ver README.")
    yield


app = FastAPI(title="Gym-bro", lifespan=lifespan)
# Los routers van antes del montaje en "/", que atrapa todo lo que llega después.
app.include_router(me.router)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
