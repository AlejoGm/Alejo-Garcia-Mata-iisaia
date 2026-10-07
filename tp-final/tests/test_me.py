from datetime import date, timedelta
from unittest.mock import patch

from tests.conftest import PROFILE, auth


def test_config_is_public_and_dev_without_auth0(client):
    response = client.get("/api/config")
    assert response.status_code == 200
    assert response.json()["auth"] == "dev"


def test_no_token_is_401(client):
    assert client.get("/api/me").status_code == 401


def test_malformed_token_is_401(client):
    assert client.get("/api/me", headers={"Authorization": "Bearer dev:"}).status_code == 401
    assert client.get("/api/me", headers={"Authorization": "Bearer xyz"}).status_code == 401


def test_without_profile_is_409(client):
    response = client.get("/api/me", headers=auth("ana"))
    assert response.status_code == 409
    assert response.json()["detail"] == "perfil incompleto"


def test_create_profile(client):
    response = client.put("/api/me", json=PROFILE, headers=auth("ana"))
    assert response.status_code == 200
    body = response.json()
    assert body["display_name"] == "Ana"
    assert body["weekly_goal"] == 3
    assert client.get("/api/me", headers=auth("ANA")).json()["id"] == body["id"]


def test_invalid_profile_is_422(client):
    for bad in ({**PROFILE, "sex": "X"}, {**PROFILE, "weekly_goal": 8}, {**PROFILE, "display_name": " "},
                {**PROFILE, "unit": "st"}):
        assert client.put("/api/me", json=bad, headers=auth("ana")).status_code == 422


def test_goal_change_applies_next_week(client):
    client.put("/api/me", json=PROFILE, headers=auth("ana"))
    body = client.put("/api/me", json={**PROFILE, "weekly_goal": 5}, headers=auth("ana")).json()

    assert body["weekly_goal"] == 3
    assert body["next_week_goal"] == 5


def test_second_change_same_week_overrides_first(client):
    client.put("/api/me", json=PROFILE, headers=auth("ana"))
    client.put("/api/me", json={**PROFILE, "weekly_goal": 5}, headers=auth("ana"))
    body = client.put("/api/me", json={**PROFILE, "weekly_goal": 4}, headers=auth("ana")).json()

    assert body["next_week_goal"] == 4


def test_goal_change_is_in_force_after_monday(client):
    client.put("/api/me", json=PROFILE, headers=auth("ana"))
    client.put("/api/me", json={**PROFILE, "weekly_goal": 5}, headers=auth("ana"))
    next_week = date.today() + timedelta(days=7)

    with patch("backend.routes.me.date") as fake_date:
        fake_date.today.return_value = next_week
        assert client.get("/api/me", headers=auth("ana")).json()["weekly_goal"] == 5


def test_dev_token_accepts_encoded_non_ascii_names(client):
    headers = {"Authorization": "Bearer dev:Luc%C3%ADa"}
    response = client.put("/api/me", json={**PROFILE, "display_name": "Lucía"}, headers=headers)
    assert response.status_code == 200
    assert client.get("/api/me", headers={"Authorization": "Bearer dev:luc%C3%ADa"}).json()["display_name"] == "Lucía"
