from datetime import date, timedelta

from tests.conftest import exercise_id
from tests.test_rankings_api import setup_group
from tests.test_sessions import post


def test_dashboard_shape_and_numbers(client):
    code, users = setup_group(client)
    squat = exercise_id(client, users["ana"], "Sentadilla")
    post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 100, "reps": 5}])
    post(client, users["beto"], [{"exercise_id": squat, "weight_kg": 80, "reps": 5}])

    body = client.get(f"/api/groups/{code}/dashboard", headers=users["ana"]).json()
    assert body["sessions"] == 2
    assert body["volume"] == 900
    assert len(body["series"]) == 8
    assert len(body["days"]) == 7
    today = next(d for d in body["days"] if d["day"] == date.today().isoformat())
    assert (today["members"], today["mine"]) == (2, True)
    assert body["leaders"][0]["exercise"] == "Sentadilla"
    assert body["goal_pct"] is not None


def test_dashboard_counts_prs_of_the_month(client):
    code, users = setup_group(client)
    bench = exercise_id(client, users["ana"], "Press banca")
    yesterday = date.today() - timedelta(days=1)
    post(client, users["ana"], [{"exercise_id": bench, "weight_kg": 80, "reps": 5}], day=yesterday)
    post(client, users["ana"], [{"exercise_id": bench, "weight_kg": 85, "reps": 5}])
    body = client.get(f"/api/groups/{code}/dashboard", headers=users["ana"]).json()
    assert body["prs_month"] + body["prs_prev_month"] == 1


def test_dashboard_requires_membership(client):
    code, _users = setup_group(client)
    from tests.conftest import register
    outsider = register(client, "zoe")
    assert client.get(f"/api/groups/{code}/dashboard", headers=outsider).status_code == 403
