from datetime import date

from tests.conftest import exercise_id, register
from tests.test_sessions import post


def test_personal_stats_default_to_most_used_exercise(client):
    ana = register(client, "ana")
    squat, bench = exercise_id(client, ana, "Sentadilla"), exercise_id(client, ana, "Press banca")
    post(client, ana, [{"exercise_id": squat, "weight_kg": 100, "reps": 5}, {"exercise_id": squat, "weight_kg": 110, "reps": 1},
                       {"exercise_id": bench, "weight_kg": 70, "reps": 5}], bodyweight=81)

    body = client.get("/api/me/stats", headers=ana).json()
    assert body["exercise_id"] == squat
    assert [e["name"] for e in body["exercises"]] == ["Sentadilla", "Press banca"]
    assert len(body["months"]) == 6
    assert body["months"][-1]["best"] == 116.7
    assert body["best_weight_kg"] == 110
    assert body["bodyweight"][-1]["kg"] == 81
    assert body["sessions"] == 1


def test_personal_stats_for_a_chosen_exercise_and_invalid_period(client):
    ana = register(client, "ana")
    bench = exercise_id(client, ana, "Press banca")
    post(client, ana, [{"exercise_id": bench, "weight_kg": 70, "reps": 1}])
    body = client.get(f"/api/me/stats?exercise_id={bench}&period=month&month={date.today():%Y-%m}", headers=ana).json()
    assert body["months"] == [{"month": f"{date.today():%Y-%m}-01", "best": 70.0, "average": 70.0}]
    assert client.get("/api/me/stats?period=custom&from=2026-09&to=2026-01", headers=ana).status_code == 422


def test_personal_stats_without_sessions(client):
    ana = register(client, "ana")
    body = client.get("/api/me/stats", headers=ana).json()
    assert body["exercise_id"] is None
    assert body["months"] == []
