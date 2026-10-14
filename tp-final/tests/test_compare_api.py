from datetime import date, timedelta

from tests.conftest import exercise_id
from tests.test_rankings_api import setup_group
from tests.test_sessions import post


def test_compare_lines_per_member(client):
    code, users = setup_group(client)
    squat = exercise_id(client, users["ana"], "Sentadilla")
    post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 100, "reps": 1}], bodyweight=90)
    post(client, users["beto"], [{"exercise_id": squat, "weight_kg": 90, "reps": 1}], bodyweight=60)
    post(client, users["beto"], [{"exercise_id": squat, "weight_kg": 80, "reps": 1}],
         day=date.today() - timedelta(days=7), bodyweight=60)

    body = client.get(f"/api/groups/{code}/compare", params={"metric": "1rm"}, headers=users["ana"]).json()

    assert body["exercise_id"] == squat  # el más cargado del grupo
    assert [e["name"] for e in body["exercises"]] == ["Sentadilla"]
    assert len(body["months"]) == 6
    lines = {p["display_name"]: p for p in body["people"]}
    assert lines["ana"]["months"][-1] == 100
    assert lines["caro"]["months"] == [None] * 6
    assert len(body["weeks"]) == 12
    assert lines["beto"]["days"][-1] == 1


def test_compare_rejects_unknown_metric(client):
    code, users = setup_group(client)
    assert client.get(f"/api/groups/{code}/compare", params={"metric": "x"}, headers=users["ana"]).status_code == 422


def test_compare_max_weight_includes_exercises_without_1rm(client):
    code, users = setup_group(client)
    curl = exercise_id(client, users["ana"], "Curl de bíceps")
    post(client, users["ana"], [{"exercise_id": curl, "weight_kg": 15, "reps": 15}])
    body = client.get(f"/api/groups/{code}/compare", params={"metric": "max"}, headers=users["ana"]).json()
    assert body["exercise_id"] == curl
    assert next(p for p in body["people"] if p["display_name"] == "ana")["months"][-1] == 15


def test_compare_includes_the_best_of_each_week(client):
    code, users = setup_group(client)
    squat = exercise_id(client, users["ana"], "Sentadilla")
    last_week = date.today() - timedelta(days=7)
    post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 90, "reps": 3}], day=last_week)
    post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 95, "reps": 3}])
    body = client.get(f"/api/groups/{code}/compare", params={"metric": "max"}, headers=users["ana"]).json()
    ana = next(p for p in body["people"] if p["display_name"] == "ana")
    assert len(ana["week_best"]) == len(body["best_weeks"])
    assert ana["week_best"][-2:] == [90, 95]
    assert body["best_weeks"][-1] == (date.today() - timedelta(days=date.today().weekday())).isoformat()
