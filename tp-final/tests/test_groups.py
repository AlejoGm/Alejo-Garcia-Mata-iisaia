from tests.conftest import exercise_id, make_group, register


def test_creator_is_admin_with_four_default_challenges(client):
    ana = register(client, "ana")
    code = make_group(client, ana)
    group = client.get(f"/api/groups/{code}", headers=ana).json()

    assert group["is_admin"] is True
    assert [c["name"] for c in group["challenges"]] == ["Sentadilla", "Press banca", "Peso muerto", "Press militar"]


def test_join_with_code_in_lowercase(client):
    ana, beto = register(client, "ana"), register(client, "beto")
    code = make_group(client, ana)

    response = client.post(f"/api/groups/{code.lower()}/join", headers=beto)
    assert response.status_code == 201
    assert response.json()["members"] == 2
    assert [g["code"] for g in client.get("/api/me/groups", headers=beto).json()] == [code]


def test_join_twice_is_409_and_unknown_group_is_404(client):
    ana, beto = register(client, "ana"), register(client, "beto")
    code = make_group(client, ana)
    client.post(f"/api/groups/{code}/join", headers=beto)

    assert client.post(f"/api/groups/{code}/join", headers=beto).status_code == 409
    assert client.post("/api/groups/ZZZZZZ/join", headers=beto).status_code == 404


def test_non_member_cannot_see_the_group(client):
    ana, beto = register(client, "ana"), register(client, "beto")
    code = make_group(client, ana)

    assert client.get(f"/api/groups/{code}", headers=beto).status_code == 403


def test_admin_leaving_passes_role_to_oldest_member(client):
    ana, beto, caro = register(client, "ana"), register(client, "beto"), register(client, "caro")
    code = make_group(client, ana)
    client.post(f"/api/groups/{code}/join", headers=beto)
    client.post(f"/api/groups/{code}/join", headers=caro)

    assert client.delete(f"/api/groups/{code}/members/me", headers=ana).status_code == 204
    assert client.get(f"/api/groups/{code}", headers=beto).json()["is_admin"] is True
    assert client.get(f"/api/groups/{code}", headers=caro).json()["is_admin"] is False


def test_only_admin_kicks_members(client):
    ana, beto = register(client, "ana"), register(client, "beto")
    code = make_group(client, ana)
    client.post(f"/api/groups/{code}/join", headers=beto)
    members = client.get(f"/api/groups/{code}", headers=ana).json()["members"]
    ana_id, beto_id = members[0]["user_id"], members[1]["user_id"]

    assert client.delete(f"/api/groups/{code}/members/{ana_id}", headers=beto).status_code == 403
    assert client.delete(f"/api/groups/{code}/members/{ana_id}", headers=ana).status_code == 422
    assert client.delete(f"/api/groups/{code}/members/{beto_id}", headers=ana).status_code == 204
    assert client.delete(f"/api/groups/{code}/members/{beto_id}", headers=ana).status_code == 404
    assert client.get(f"/api/groups/{code}", headers=beto).status_code == 403


def test_challenges_admin_only_and_max_four(client):
    ana, beto = register(client, "ana"), register(client, "beto")
    code = make_group(client, ana)
    client.post(f"/api/groups/{code}/join", headers=beto)
    ids = [exercise_id(client, ana, n) for n in ("Dominadas", "Hip thrust")]

    assert client.put(f"/api/groups/{code}/challenges", json={"exercise_ids": ids}, headers=beto).status_code == 403
    response = client.put(f"/api/groups/{code}/challenges", json={"exercise_ids": ids}, headers=ana)
    assert [c["name"] for c in response.json()] == ["Dominadas", "Hip thrust"]
    assert client.put(f"/api/groups/{code}/challenges", json={"exercise_ids": [1, 2, 3, 4, 5]},
                      headers=ana).status_code == 422
    assert client.put(f"/api/groups/{code}/challenges", json={"exercise_ids": [9999]}, headers=ana).status_code == 422


def test_exercise_names_are_unique_ignoring_case(client):
    ana = register(client, "ana")
    assert client.post("/api/exercises", json={"name": "sentadilla"}, headers=ana).status_code == 409
    response = client.post("/api/exercises", json={"name": "Muscle up", "bodyweight": True}, headers=ana)
    assert response.status_code == 201
    assert response.json()["bodyweight"] is True


def test_catalog_names_are_unique_and_seed_is_idempotent(client):
    from backend.catalog import EXERCISES
    ana = register(client, "ana")
    names = [e["name"] for e in client.get("/api/exercises", headers=ana).json()]
    assert len(names) == len(EXERCISES)
    assert len({n.lower() for n in names}) == len(names)
