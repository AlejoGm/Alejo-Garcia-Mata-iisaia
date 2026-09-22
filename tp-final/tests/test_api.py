from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from backend.db import get_session
from backend.main import app


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


def create_group(client, name="Los del gym"):
    response = client.post("/api/groups", json={"name": name})
    assert response.status_code == 201
    return response.json()["code"]


def join(client, code, nickname, bodyweight):
    return client.post(f"/api/groups/{code}/members", json={"nickname": nickname, "bodyweight_kg": bodyweight})


def exercise_id(client, code, name):
    exercises = client.get(f"/api/groups/{code}").json()["exercises"]
    return next(e["id"] for e in exercises if e["name"] == name)


def post_session(client, code, nickname, sets, day=None):
    body = {"date": (day or date.today()).isoformat(), "sets": sets}
    return client.post(f"/api/groups/{code}/members/{nickname}/sessions", json=body)


def test_new_group_has_a_six_char_code_and_four_challenges(client):
    code = create_group(client)
    group = client.get(f"/api/groups/{code}").json()

    assert len(code) == 6
    assert group["name"] == "Los del gym"
    assert [e["name"] for e in group["exercises"] if e["is_challenge"]] == [
        "Sentadilla", "Press banca", "Peso muerto", "Press militar",
    ]


def test_unknown_group_is_404(client):
    assert client.get("/api/groups/ZZZZZZ").status_code == 404
    assert join(client, "ZZZZZZ", "ana", 60).status_code == 404


def test_join_group(client):
    code = create_group(client)
    response = join(client, code, "Ana", 60)

    assert response.status_code == 201
    assert response.json() == {"nickname": "Ana", "bodyweight_kg": 60}
    assert client.get(f"/api/groups/{code}").json()["members"] == [{"nickname": "Ana", "bodyweight_kg": 60}]


def test_nickname_taken_ignores_case(client):
    code = create_group(client)
    join(client, code, "Ana", 60)

    assert join(client, code, "ana", 70).status_code == 409


@pytest.mark.parametrize("nickname, bodyweight", [("", 60), ("x" * 21, 60), ("ana", 0), ("ana", 301)])
def test_invalid_member_is_422(client, nickname, bodyweight):
    code = create_group(client)
    assert join(client, code, nickname, bodyweight).status_code == 422


def test_session_returns_estimated_1rm_per_set(client):
    code = create_group(client)
    join(client, code, "ana", 60)
    squat = exercise_id(client, code, "Sentadilla")

    response = post_session(client, code, "ana", [
        {"exercise_id": squat, "weight_kg": 100, "reps": 1},
        {"exercise_id": squat, "weight_kg": 60, "reps": 12},
    ])

    assert response.status_code == 201
    sets = response.json()["sets"]
    assert sets[0]["exercise"] == "Sentadilla"
    assert sets[0]["estimated_1rm"] == 100
    assert sets[1]["estimated_1rm"] is None


def test_session_for_unknown_member_is_404(client):
    code = create_group(client)
    squat = exercise_id(client, code, "Sentadilla")

    assert post_session(client, code, "nadie", [{"exercise_id": squat, "weight_kg": 100, "reps": 1}]).status_code == 404


def test_exercise_from_another_group_is_422(client):
    code = create_group(client)
    other = create_group(client, "Otro")
    join(client, code, "ana", 60)
    foreign = exercise_id(client, other, "Sentadilla")

    assert post_session(client, code, "ana", [{"exercise_id": foreign, "weight_kg": 100, "reps": 1}]).status_code == 422


@pytest.mark.parametrize("weight, reps", [(0, 5), (501, 5), (100, 0), (100, 51)])
def test_impossible_set_is_422(client, weight, reps):
    code = create_group(client)
    join(client, code, "ana", 60)
    squat = exercise_id(client, code, "Sentadilla")

    assert post_session(client, code, "ana", [{"exercise_id": squat, "weight_kg": weight, "reps": reps}]).status_code == 422


def test_future_date_or_empty_session_is_422(client):
    code = create_group(client)
    join(client, code, "ana", 60)
    squat = exercise_id(client, code, "Sentadilla")
    tomorrow = date.today() + timedelta(days=1)

    assert post_session(client, code, "ana", [{"exercise_id": squat, "weight_kg": 100, "reps": 1}], tomorrow).status_code == 422
    assert post_session(client, code, "ana", []).status_code == 422


def test_strength_ranking_is_relative_to_bodyweight(client):
    code = create_group(client)
    join(client, code, "ana", 50)
    join(client, code, "beto", 100)
    join(client, code, "caro", 70)
    squat = exercise_id(client, code, "Sentadilla")
    post_session(client, code, "ana", [{"exercise_id": squat, "weight_kg": 100, "reps": 1}])
    post_session(client, code, "beto", [{"exercise_id": squat, "weight_kg": 150, "reps": 1}])

    strength = client.get(f"/api/groups/{code}/rankings").json()["strength"]
    squat_ranking = next(r for r in strength if r["exercise"] == "Sentadilla")

    assert [e["nickname"] for e in squat_ranking["entries"]] == ["ana", "beto", "caro"]
    assert squat_ranking["entries"][0]["ratio"] == 2.0
    assert squat_ranking["entries"][2]["ratio"] is None
