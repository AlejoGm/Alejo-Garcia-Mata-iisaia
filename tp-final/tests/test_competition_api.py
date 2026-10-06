from datetime import date, timedelta
from unittest.mock import patch

from tests.conftest import exercise_id
from tests.test_rankings_api import setup_group
from tests.test_sessions import post


def ids(client, code, headers):
    return {m["display_name"]: m["user_id"] for m in client.get(f"/api/groups/{code}", headers=headers).json()["members"]}


def test_duel_flow_challenge_accept_and_result(client):
    code, users = setup_group(client)
    members = ids(client, code, users["ana"])
    squat = exercise_id(client, users["ana"], "Sentadilla")
    duel = client.post(f"/api/groups/{code}/duels", headers=users["ana"],
                       json={"opponent_id": members["beto"], "exercise_id": squat, "mode": "absolute", "days": 3}).json()
    assert duel["status"] == "pending"

    assert client.post(f"/api/groups/{code}/duels/{duel['id']}/accept", headers=users["ana"]).status_code == 403
    accepted = client.post(f"/api/groups/{code}/duels/{duel['id']}/accept", headers=users["beto"]).json()
    assert accepted["status"] == "active"
    assert client.post(f"/api/groups/{code}/duels/{duel['id']}/reject", headers=users["beto"]).status_code == 409

    post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 120, "reps": 3}])
    post(client, users["beto"], [{"exercise_id": squat, "weight_kg": 110, "reps": 5}])
    listed = client.get(f"/api/groups/{code}/duels", headers=users["caro"]).json()[0]
    assert (listed["challenger_value"], listed["opponent_value"], listed["winner_id"]) == (120, 110, members["ana"])


def test_duel_validations(client):
    code, users = setup_group(client)
    members = ids(client, code, users["ana"])
    squat = exercise_id(client, users["ana"], "Sentadilla")
    body = {"opponent_id": members["beto"], "exercise_id": squat, "mode": "dots", "days": 7}
    assert client.post(f"/api/groups/{code}/duels", json={**body, "opponent_id": members["ana"]},
                       headers=users["ana"]).status_code == 422
    assert client.post(f"/api/groups/{code}/duels", json={**body, "days": 5}, headers=users["ana"]).status_code == 422
    assert client.post(f"/api/groups/{code}/duels", json=body, headers=users["ana"]).status_code == 201
    assert client.post(f"/api/groups/{code}/duels", json={**body, "opponent_id": members["ana"]},
                       headers=users["beto"]).status_code == 409


def test_suggestions_ordered_by_imbalance(client):
    code, users = setup_group(client)
    squat = exercise_id(client, users["ana"], "Sentadilla")
    for name, kg in (("ana", 100), ("beto", 70), ("caro", 95)):
        post(client, users[name], [{"exercise_id": squat, "weight_kg": kg, "reps": 1}])
    body = client.get(f"/api/groups/{code}/duels/suggestions?exercise_id={squat}&mode=absolute",
                      headers=users["ana"]).json()
    assert body["mine"] == 100
    assert [(r["display_name"], r["level"]) for r in body["rivals"]] == [("caro", "low"), ("beto", "high")]


def test_campaign_admin_only_and_winner_frozen_after_end(client):
    code, users = setup_group(client)
    squat = exercise_id(client, users["ana"], "Sentadilla")
    today = date.today()
    body = {"name": "Verano", "start": (today - timedelta(days=3)).isoformat(), "end": today.isoformat(),
            "tables": [f"absolute:{squat}", "progress"]}
    assert client.post(f"/api/groups/{code}/campaigns", json=body, headers=users["beto"]).status_code == 403
    assert client.post(f"/api/groups/{code}/campaigns", json={**body, "tables": ["nada"]},
                       headers=users["ana"]).status_code == 422
    campaign = client.post(f"/api/groups/{code}/campaigns", json=body, headers=users["ana"]).json()
    assert campaign["table_labels"] == ["Absoluto Sentadilla", "Progreso"]
    post(client, users["beto"], [{"exercise_id": squat, "weight_kg": 120, "reps": 1}])
    post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 100, "reps": 1}])

    live = client.get(f"/api/groups/{code}/campaigns", headers=users["caro"]).json()[0]
    assert live["status"] == "active"
    assert [(s["display_name"], s["points"]) for s in live["standings"]][:2] == [("beto", 10), ("ana", 8)]
    assert live["winner"] is None

    with patch("backend.routes.campaigns.date") as fake:
        fake.today.return_value = today + timedelta(days=1)
        closed = client.get(f"/api/groups/{code}/campaigns", headers=users["caro"]).json()[0]
    assert closed["status"] == "finished"
    assert closed["winner"]["display_name"] == "beto"
