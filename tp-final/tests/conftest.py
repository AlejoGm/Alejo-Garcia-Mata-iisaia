import os

os.environ.pop("AUTH0_DOMAIN", None)
os.environ["GYMBRO_DB"] = ":memory:"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402
from sqlmodel.pool import StaticPool  # noqa: E402

from backend import config  # noqa: E402
from backend.db import get_session  # noqa: E402
from backend.main import app  # noqa: E402

config.AUTH_MODE = "dev"

PROFILE = {"display_name": "Ana", "sex": "F", "weekly_goal": 3, "unit": "kg"}


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def auth(name: str) -> dict:
    return {"Authorization": f"Bearer dev:{name}"}


def register(client, name: str, sex: str = "M", goal: int = 3) -> dict:
    headers = auth(name)
    response = client.put("/api/me", json={"display_name": name, "sex": sex, "weekly_goal": goal}, headers=headers)
    assert response.status_code == 200, response.text
    return headers
