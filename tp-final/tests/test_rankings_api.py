from datetime import date, timedelta

from tests.conftest import exercise_id, make_group, register
from tests.test_sessions import post


def setup_group(client, names=("ana", "beto", "caro")):
    users = {n: register(client, n) for n in names}
    code = make_group(client, users[names[0]])
    for n in names[1:]:
        client.post(f"/api/groups/{code}/join", headers=users[n])
    return code, users


def test_rankings_shape_and_dots_order(client):
    code, users = setup_group(client)
    squat = exercise_id(client, users["ana"], "Sentadilla")
    post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 170, "reps": 1}], bodyweight=95)
    post(client, users["beto"], [{"exercise_id": squat, "weight_kg": 130, "reps": 1}], bodyweight=65)

    body = client.get(f"/api/groups/{code}/rankings", headers=users["ana"]).json()
    squat_row = next(s for s in body["strength"] if s["exercise"] == "Sentadilla")
    assert [r["display_name"] for r in squat_row["dots"]] == ["ana", "beto", "caro"]
    assert squat_row["dots"][2]["value"] is None
    assert [r["display_name"] for r in squat_row["absolute"]][:2] == ["ana", "beto"]
    assert {r["display_name"] for r in body["weekly"]} == {"ana", "beto", "caro"}
    assert body["period"]["kind"] == "month"


def test_invalid_period_is_422_and_non_member_403(client):
    code, users = setup_group(client)
    outsider = register(client, "zoe")
    assert client.get(f"/api/groups/{code}/rankings?period=custom&from=2026-05&to=2026-01",
                      headers=users["ana"]).status_code == 422
    assert client.get(f"/api/groups/{code}/rankings?period=eterno", headers=users["ana"]).status_code == 422
    assert client.get(f"/api/groups/{code}/rankings", headers=outsider).status_code == 403


def test_feed_lists_prs_and_reactions(client):
    code, users = setup_group(client)
    bench = exercise_id(client, users["ana"], "Press banca")
    post(client, users["ana"], [{"exercise_id": bench, "weight_kg": 80, "reps": 5}], day=date.today() - timedelta(days=2))
    pr_set = post(client, users["ana"], [{"exercise_id": bench, "weight_kg": 85, "reps": 5}]).json()["sets"][0]["id"]

    assert client.put(f"/api/groups/{code}/feed/{pr_set}/reaction", json={"kind": "fuego"},
                      headers=users["beto"]).status_code == 200
    client.put(f"/api/groups/{code}/feed/{pr_set}/reaction", json={"kind": "fuerza"}, headers=users["beto"])
    feed = client.get(f"/api/groups/{code}/feed", headers=users["beto"]).json()

    assert len(feed) == 1
    assert feed[0]["pr"] == "weight"
    assert feed[0]["reactions"] == {"fuerza": 1, "fuego": 0, "dudoso": 0}
    assert feed[0]["mine"] == "fuerza"
    assert client.delete(f"/api/groups/{code}/feed/{pr_set}/reaction", headers=users["beto"]).status_code == 204
    assert client.get(f"/api/groups/{code}/feed", headers=users["beto"]).json()[0]["mine"] is None


def test_reacting_to_a_set_that_is_not_a_pr_is_404(client):
    code, users = setup_group(client)
    bench = exercise_id(client, users["ana"], "Press banca")
    first = post(client, users["ana"], [{"exercise_id": bench, "weight_kg": 80, "reps": 5}]).json()["sets"][0]["id"]
    assert client.put(f"/api/groups/{code}/feed/{first}/reaction", json={"kind": "fuego"},
                      headers=users["beto"]).status_code == 404
    assert client.put(f"/api/groups/{code}/feed/{first}/reaction", json={"kind": "meh"},
                      headers=users["beto"]).status_code == 422


def test_majority_dudoso_excludes_the_set_from_rankings(client):
    code, users = setup_group(client)
    squat = exercise_id(client, users["ana"], "Sentadilla")
    post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 100, "reps": 1}], day=date.today() - timedelta(days=1))
    fake = post(client, users["ana"], [{"exercise_id": squat, "weight_kg": 300, "reps": 1}]).json()["sets"][0]["id"]

    for name in ("beto", "caro"):
        client.put(f"/api/groups/{code}/feed/{fake}/reaction", json={"kind": "dudoso"}, headers=users[name])

    body = client.get(f"/api/groups/{code}/rankings?period=all", headers=users["ana"]).json()
    squat_row = next(s for s in body["strength"] if s["exercise"] == "Sentadilla")
    assert squat_row["absolute"][0]["value"] == 100
    assert client.get(f"/api/groups/{code}/feed", headers=users["ana"]).json()[0]["excluded"] is True
