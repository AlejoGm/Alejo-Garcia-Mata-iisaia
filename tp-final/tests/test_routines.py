from tests.conftest import exercise_id, make_group, register


def push_pull(client, headers):
    bench, row = exercise_id(client, headers, "Press banca"), exercise_id(client, headers, "Remo con barra")
    return {"name": "Push/Pull", "days": [
        {"name": "Push", "items": [{"exercise_id": bench, "sets": 3}]},
        {"name": "Pull", "items": [{"exercise_id": row, "sets": 4}]},
    ]}


def group_with_two(client):
    ana, beto = register(client, "ana"), register(client, "beto")
    code = make_group(client, ana)
    client.post(f"/api/groups/{code}/join", headers=beto)
    return code, ana, beto


def test_create_list_and_follow(client):
    code, ana, beto = group_with_two(client)
    routine = client.post(f"/api/groups/{code}/routines", json=push_pull(client, ana), headers=ana).json()
    assert [d["name"] for d in routine["days"]] == ["Push", "Pull"]

    assert client.put(f"/api/groups/{code}/members/me/routine", json={"routine_id": routine["id"]},
                      headers=beto).status_code == 200
    listed = client.get(f"/api/groups/{code}/routines", headers=ana).json()
    assert listed[0]["followers"] == [routine["created_by"] + 1]
    group = client.get(f"/api/groups/{code}", headers=beto).json()
    assert next(m for m in group["members"] if m["display_name"] == "beto")["routine_id"] == routine["id"]


def test_invalid_routines_are_422(client):
    code, ana, _ = group_with_two(client)
    body = push_pull(client, ana)
    assert client.post(f"/api/groups/{code}/routines", json={**body, "days": []}, headers=ana).status_code == 422
    body["days"][0]["items"][0]["sets"] = 11
    assert client.post(f"/api/groups/{code}/routines", json=body, headers=ana).status_code == 422
    body["days"][0]["items"][0] = {"exercise_id": 9999, "sets": 3}
    assert client.post(f"/api/groups/{code}/routines", json=body, headers=ana).status_code == 422


def test_routine_of_another_group_is_404_and_cannot_be_followed(client):
    code, ana, _ = group_with_two(client)
    other = make_group(client, ana, "Otro")
    routine = client.post(f"/api/groups/{other}/routines", json=push_pull(client, ana), headers=ana).json()
    assert client.put(f"/api/groups/{code}/routines/{routine['id']}", json=push_pull(client, ana),
                      headers=ana).status_code == 404
    assert client.put(f"/api/groups/{code}/members/me/routine", json={"routine_id": routine["id"]},
                      headers=ana).status_code == 422


def test_replacing_a_routine_keeps_logged_sessions(client):
    code, ana, _ = group_with_two(client)
    routine = client.post(f"/api/groups/{code}/routines", json=push_pull(client, ana), headers=ana).json()
    day_id = routine["days"][0]["id"]
    bench = exercise_id(client, ana, "Press banca")
    body = {"date": "2026-10-01", "bodyweight_kg": 80, "routine_day_id": day_id,
            "sets": [{"exercise_id": bench, "weight_kg": 80, "reps": 5}]}
    assert client.post("/api/me/sessions", json=body, headers=ana).status_code == 201

    new = push_pull(client, ana) | {"name": "PPL"}
    assert client.put(f"/api/groups/{code}/routines/{routine['id']}", json=new, headers=ana).status_code == 200
    sessions = client.get("/api/me/sessions", headers=ana).json()
    assert sessions[0]["routine_day_id"] is None
    assert len(sessions[0]["sets"]) == 1


def test_deleting_a_routine_unfollows_it(client):
    code, ana, beto = group_with_two(client)
    routine = client.post(f"/api/groups/{code}/routines", json=push_pull(client, ana), headers=ana).json()
    client.put(f"/api/groups/{code}/members/me/routine", json={"routine_id": routine["id"]}, headers=beto)
    assert client.delete(f"/api/groups/{code}/routines/{routine['id']}", headers=ana).status_code == 204
    assert client.get(f"/api/groups/{code}/routines", headers=ana).json() == []
    members = client.get(f"/api/groups/{code}", headers=beto).json()["members"]
    assert all(m["routine_id"] is None for m in members)
