import pytest

from backend import config
from tests.conftest import PROFILE, register


@pytest.fixture
def local(monkeypatch):
    monkeypatch.setattr(config, "AUTH_MODE", "local")


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def signup(client, username="ana", password="secreta123"):
    return client.post("/api/auth/register", json={"username": username, "password": password})


def test_register_then_complete_profile(client, local):
    response = signup(client)
    assert response.status_code == 201
    token = response.json()["token"]
    assert client.get("/api/me", headers=bearer(token)).status_code == 409  # falta el perfil
    assert client.put("/api/me", headers=bearer(token), json=PROFILE).status_code == 200
    assert client.get("/api/me", headers=bearer(token)).json()["display_name"] == "Ana"


def test_login_with_the_right_password_only(client, local):
    signup(client, "Ana", "secreta123")
    assert client.post("/api/auth/login", json={"username": "ana", "password": "otra"}).status_code == 401
    assert client.post("/api/auth/login", json={"username": "nadie", "password": "secreta123"}).status_code == 401
    ok = client.post("/api/auth/login", json={"username": " ANA ", "password": "secreta123"})
    assert ok.status_code == 200 and ok.json()["token"]


def test_username_taken_and_validation(client, local):
    signup(client)
    assert signup(client).status_code == 409
    assert signup(client, "x", "secreta123").status_code == 422          # usuario muy corto
    assert signup(client, "otro", "123").status_code == 422              # contraseña muy corta
    assert signup(client, "con espacio", "secreta123").status_code == 422


def test_dev_tokens_are_rejected_with_local_accounts(client, local):
    assert client.get("/api/me", headers=bearer("dev:ana")).status_code == 401


def test_registering_an_existing_dev_name_keeps_its_history(client, monkeypatch):
    register(client, "alejo")  # usuario creado antes, en modo desarrollo
    monkeypatch.setattr(config, "AUTH_MODE", "local")
    token = signup(client, "alejo").json()["token"]
    assert client.get("/api/me", headers=bearer(token)).json()["display_name"] == "alejo"


def test_logout_invalidates_the_token(client, local):
    token = signup(client).json()["token"]
    assert client.post("/api/auth/logout", headers=bearer(token)).status_code == 204
    assert client.get("/api/me", headers=bearer(token)).status_code == 401
