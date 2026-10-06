from datetime import date, timedelta

import pytest

from tests.conftest import exercise_id, make_group, register


def post(client, headers, sets, day=None, bodyweight=80):
    body = {"date": (day or date.today()).isoformat(), "bodyweight_kg": bodyweight, "sets": sets}
    return client.post("/api/me/sessions", json=body, headers=headers)


def test_session_returns_1rm_dots_and_prs(client):
    ana = register(client, "ana", sex="M")
    squat = exercise_id(client, ana, "Sentadilla")
    yesterday = date.today() - timedelta(days=1)
    post(client, ana, [{"exercise_id": squat, "weight_kg": 100, "reps": 1}], day=yesterday)

    response = post(client, ana, [
        {"exercise_id": squat, "weight_kg": 105, "reps": 1},
        {"exercise_id": squat, "weight_kg": 95, "reps": 8},
    ], bodyweight=95)

    assert response.status_code == 201
    sets = response.json()["sets"]
    assert sets[0]["pr"] == "weight"
    assert sets[1]["pr"] == "1rm"
    assert sets[1]["estimated_1rm"] == pytest.approx(120.3, abs=0.05)
    assert sets[0]["dots"] == pytest.approx(66.1, abs=0.1)


def test_bodyweight_exercise_accepts_zero_lastre(client):
    ana = register(client, "ana")
    pullup = exercise_id(client, ana, "Dominadas")
    squat = exercise_id(client, ana, "Sentadilla")

    response = post(client, ana, [{"exercise_id": pullup, "weight_kg": 0, "reps": 8}], bodyweight=75)
    assert response.status_code == 201
    assert response.json()["sets"][0]["load"] == 75
    assert post(client, ana, [{"exercise_id": squat, "weight_kg": 0, "reps": 8}]).status_code == 422


@pytest.mark.parametrize("weight, reps, bodyweight", [(501, 5, 80), (100, 0, 80), (100, 51, 80), (100, 5, 20)])
def test_impossible_values_are_422(client, weight, reps, bodyweight):
    ana = register(client, "ana")
    squat = exercise_id(client, ana, "Sentadilla")
    assert post(client, ana, [{"exercise_id": squat, "weight_kg": weight, "reps": reps}],
                bodyweight=bodyweight).status_code == 422


def test_future_date_empty_session_or_unknown_exercise_are_422(client):
    ana = register(client, "ana")
    squat = exercise_id(client, ana, "Sentadilla")
    tomorrow = date.today() + timedelta(days=1)
    assert post(client, ana, [{"exercise_id": squat, "weight_kg": 100, "reps": 1}], day=tomorrow).status_code == 422
    assert post(client, ana, []).status_code == 422
    assert post(client, ana, [{"exercise_id": 9999, "weight_kg": 100, "reps": 1}]).status_code == 422


def test_profile_prefills_last_bodyweight(client):
    ana = register(client, "ana")
    squat = exercise_id(client, ana, "Sentadilla")
    post(client, ana, [{"exercise_id": squat, "weight_kg": 100, "reps": 1}], bodyweight=82.5)
    assert client.get("/api/me", headers=ana).json()["last_bodyweight_kg"] == 82.5


def test_history_and_delete_only_mine(client):
    ana, beto = register(client, "ana"), register(client, "beto")
    squat = exercise_id(client, ana, "Sentadilla")
    session_id = post(client, ana, [{"exercise_id": squat, "weight_kg": 100, "reps": 1}]).json()["id"]

    assert [s["id"] for s in client.get("/api/me/sessions", headers=ana).json()] == [session_id]
    assert client.delete(f"/api/me/sessions/{session_id}", headers=beto).status_code == 404
    assert client.delete(f"/api/me/sessions/{session_id}", headers=ana).status_code == 204
    assert client.get("/api/me/sessions", headers=ana).json() == []


def test_last_shows_my_top_set_and_up_to_two_others(client):
    users = [register(client, n) for n in ("ana", "beto", "caro", "dani")]
    code = make_group(client, users[0])
    for headers in users[1:]:
        client.post(f"/api/groups/{code}/join", headers=headers)
    bench = exercise_id(client, users[0], "Press banca")
    for i, headers in enumerate(users):
        post(client, headers, [{"exercise_id": bench, "weight_kg": 60 + i, "reps": 8},
                               {"exercise_id": bench, "weight_kg": 70 + i, "reps": 5}],
             day=date.today() - timedelta(days=i))

    body = client.get(f"/api/groups/{code}/last", params={"exercise_id": bench}, headers=users[0]).json()
    assert body["mine"]["weight_kg"] == 70
    assert [o["display_name"] for o in body["others"]] == ["beto", "caro"]
