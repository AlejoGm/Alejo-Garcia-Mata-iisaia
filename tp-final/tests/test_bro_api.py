from tests.conftest import exercise_id, register
from tests.test_rankings_api import setup_group
from tests.test_sessions import post


def test_member_profile_with_face_off_and_sessions(client):
    code, users = setup_group(client)
    squat = exercise_id(client, users["ana"], "Sentadilla")
    post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 100, "reps": 1}], bodyweight=90)
    post(client, users["beto"], [{"exercise_id": squat, "weight_kg": 90, "reps": 1}], bodyweight=60)
    beto_id = client.get("/api/me", headers=users["beto"]).json()["id"]

    body = client.get(f"/api/groups/{code}/members/{beto_id}", headers=users["ana"]).json()

    assert body["display_name"] == "beto"
    assert body["is_me"] is False
    assert body["week_days"] == 1
    assert len(body["achievements"]) == 11
    assert body["faceoff"] == [{"exercise_id": squat, "exercise": "Sentadilla", "mine_1rm": 100, "theirs_1rm": 90,
                                "mine_dots": body["faceoff"][0]["mine_dots"],
                                "theirs_dots": body["faceoff"][0]["theirs_dots"], "winner": "theirs"}]
    assert body["sessions"][0]["sets"] == 1
    assert body["sessions"][0]["exercises"] == ["Sentadilla"]


def test_member_profile_404_for_someone_outside_the_group(client):
    code, users = setup_group(client)
    outsider = register(client, "zoe")
    zoe_id = client.get("/api/me", headers=outsider).json()["id"]
    assert client.get(f"/api/groups/{code}/members/{zoe_id}", headers=users["ana"]).status_code == 404
    assert client.get(f"/api/groups/{code}/members/{zoe_id}", headers=outsider).status_code == 403
