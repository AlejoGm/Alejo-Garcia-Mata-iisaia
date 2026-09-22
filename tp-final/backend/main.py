from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.db import create_tables
from backend.routes import router

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_tables()
    yield


app = FastAPI(title="Gym-bro", lifespan=lifespan)
# El router va antes del montaje en "/", que atrapa todo lo que llega después.
app.include_router(router)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
