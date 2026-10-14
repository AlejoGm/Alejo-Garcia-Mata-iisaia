from datetime import date, timedelta

from tests.conftest import exercise_id
from tests.test_rankings_api import setup_group
from tests.test_sessions import post


def test_live_standing_without_saving(client):
    code, users = setup_group(client)
    bench = exercise_id(client, users["ana"], "Press banca")
    yesterday = date.today() - timedelta(days=1)
    post(client, users["ana"], [{"exercise_id": bench, "weight_kg": 80, "reps": 5}], day=yesterday, bodyweight=80)
    post(client, users["beto"], [{"exercise_id": bench, "weight_kg": 90, "reps": 5}], day=yesterday, bodyweight=80)
    post(client, users["caro"], [{"exercise_id": bench, "weight_kg": 100, "reps": 5}], day=yesterday, bodyweight=80)

    body = client.post(f"/api/groups/{code}/standing", headers=users["ana"],
                       json={"exercise_id": bench, "weight_kg": 92.5, "reps": 5, "bodyweight_kg": 80}).json()

    assert body["pr"] == "weight"
    assert (body["position_before"], body["position"], body["total"]) == (3, 2, 3)
    assert [p["display_name"] for p in body["passed"]] == ["beto"]
    assert body["next"]["display_name"] == "caro"
    assert (body["next"]["weight_kg"], body["next"]["reps"]) == (102.5, 5)  # 100 × 5 de caro, al mismo peso corporal
    sessions = client.get("/api/me/sessions", headers=users["ana"]).json()
    assert len(sessions) == 1  # no guardó nada


def test_live_standing_without_1rm_and_validation(client):
    code, users = setup_group(client)
    bench = exercise_id(client, users["ana"], "Press banca")
    body = client.post(f"/api/groups/{code}/standing", headers=users["ana"],
                       json={"exercise_id": bench, "weight_kg": 40, "reps": 15, "bodyweight_kg": 80}).json()
    assert (body["dots"], body["position"]) == (None, None)
    bad = client.post(f"/api/groups/{code}/standing", headers=users["ana"],
                      json={"exercise_id": bench, "weight_kg": 40, "reps": 0, "bodyweight_kg": 80})
    assert bad.status_code == 422
