"""Puebla un grupo que ya existe con participantes de mentira y 8 semanas de historia. Solo en modo dev.

    uv run python -m scripts.seed_group CODIGO --as alejo

`--as` es el nombre (dev) de un miembro del grupo, para leerlo. Los participantes siguen la primera rutina
del grupo y entrenan sus días en orden; sin rutina, hacen los desafíos. Se puede correr de nuevo: los que
ya están en el grupo no se vuelven a sumar, pero sí se les agregan sesiones.
"""
import argparse
import random
from urllib.parse import quote
from datetime import date, timedelta

from fastapi.testclient import TestClient

from backend import config
from backend.main import app

FAKES = [  # nombre, sexo, peso corporal, objetivo semanal, factor de fuerza
    ("Nacho", "M", 84, 4, 1.15),
    ("Lucía", "F", 62, 3, 0.62),
    ("Tomi", "M", 74, 4, 0.95),
    ("Flor", "F", 58, 3, 0.55),
    ("Bruno", "M", 92, 5, 1.25),
]

# Carga de trabajo típica para alguien de fuerza media; se escala con el factor de cada uno.
BASE = [
    ("hack squat", 110), ("sentadilla", 100), ("peso muerto rumano", 90), ("peso muerto", 120),
    ("press banca", 80), ("press declinado", 75), ("press inclinado", 26), ("convergente", 60),
    ("press militar", 50), ("press de hombros", 22), ("press arnold", 18),
    ("aperturas en polea", 15), ("aperturas", 16), ("reverse pec deck", 35), ("pec deck", 50),
    ("elevaciones laterales en polea", 7), ("vuelos laterales", 9), ("elevaciones laterales", 9),
    ("pushdown", 27), ("overhead", 20), ("single arm", 10), ("press francés", 25), ("extensión de tríceps", 25),
    ("jalón", 60), ("remo", 60), ("pullover", 25), ("face pull", 25),
    ("hammer preacher", 14), ("preacher", 12), ("curl en polea", 25), ("curl inclinado", 12), ("curl", 14),
    ("curl femoral", 40), ("extensión de cuádriceps", 50), ("prensa", 160), ("hip thrust", 100),
    ("elevación de talones", 60), ("zancadas", 20), ("abdominales", 30),
]


def auth(name: str) -> dict:
    return {"Authorization": f"Bearer dev:{quote(name.lower())}"}


def base_weight(exercise: dict) -> float:
    if exercise["bodyweight"]:
        return 0
    name = exercise["name"].lower()
    return next((kg for key, kg in BASE if key in name), 20)


def round_plate(kg: float) -> float:
    return max(0, round(kg / 2.5) * 2.5)


def training_days(rng: random.Random, goal: int, monday: date, today: date) -> list[date]:
    count = max(1, min(6, goal + rng.choice([-1, 0, 0, 0, 1])))
    days = sorted(rng.sample(range(6), count))
    return [monday + timedelta(days=d) for d in days if monday + timedelta(days=d) <= today]


def session_sets(rng: random.Random, plan: list[tuple[dict, int]], factor: float, progress: float) -> list[dict]:
    sets = []
    for exercise, count in plan:
        top = base_weight(exercise) * factor * progress * rng.uniform(0.95, 1.05)
        for index in range(count):
            # La última serie es la más pesada: de ahí salen los PRs a medida que progresa.
            weight = top if index == count - 1 else top * rng.uniform(0.85, 0.95)
            if exercise["bodyweight"]:
                weight = rng.choice([0, 0, 2.5, 5]) * factor
            sets.append({"exercise_id": exercise["id"], "weight_kg": round_plate(weight),
                         "reps": rng.choice([6, 8, 8, 10, 12]) if index < count - 1 else rng.choice([5, 6, 8])})
    return sets


def plans_for(client: TestClient, code: str, reader: dict, group: dict) -> tuple[list, list, int | None]:
    """Un plan por día de la primera rutina del grupo (o los desafíos), el id de cada día y el de la rutina."""
    exercises = {e["id"]: e for e in client.get("/api/exercises", headers=reader).json()}
    routines = client.get(f"/api/groups/{code}/routines", headers=reader).json()
    if routines:
        days = routines[0]["days"]
        plans = [[(exercises[i["exercise_id"]], i["sets"]) for i in day["items"]] for day in days]
        return plans, [day["id"] for day in days], routines[0]["id"]
    return [[(exercises[c["id"]], 3) for c in group["challenges"]]], [None], None


def seed(code: str, reader_name: str) -> None:
    rng = random.Random(code)
    reader = auth(reader_name)
    today = date.today()
    with TestClient(app) as client:
        group = client.get(f"/api/groups/{code}", headers=reader)
        if group.status_code != 200:
            raise SystemExit(f"No se pudo leer el grupo {code} como '{reader_name}': {group.json().get('detail')}")
        group = group.json()
        plans, day_ids, routine_id = plans_for(client, code, reader, group)
        this_monday = today - timedelta(days=today.weekday())
        for position, (name, sex, bodyweight, goal, factor) in enumerate(FAKES):
            headers = auth(name)
            client.put("/api/me", headers=headers, json={"display_name": name, "sex": sex, "weekly_goal": goal})
            client.post(f"/api/groups/{code}/join", headers=headers)
            if routine_id:
                client.put(f"/api/groups/{code}/members/me/routine", headers=headers, json={"routine_id": routine_id})
            day_index = position  # cada uno arranca la rutina en un día distinto
            for week in range(8, -1, -1):
                monday = this_monday - timedelta(days=7 * week)
                for day in training_days(rng, goal, monday, today):
                    slot = day_index % len(plans)
                    sets = session_sets(rng, plans[slot], factor, 1 + (8 - week) * 0.015)
                    client.post("/api/me/sessions", headers=headers, json={
                        "date": day.isoformat(), "bodyweight_kg": round(bodyweight + rng.uniform(-0.8, 0.8), 1),
                        "routine_day_id": day_ids[slot], "sets": sets})
                    day_index += 1
        react_and_duel(client, code, rng)
        print(f"Listo: {len(FAKES)} participantes en {group['name']} ({code}) con 8 semanas de sesiones.")


def react_and_duel(client: TestClient, code: str, rng: random.Random) -> None:
    names = [f[0] for f in FAKES]
    for item in client.get(f"/api/groups/{code}/feed?limit=40", headers=auth(names[0])).json():
        for name in rng.sample(names, 2):
            if name.lower() != item["display_name"].lower():
                client.put(f"/api/groups/{code}/feed/{item['set_id']}/reaction", headers=auth(name),
                           json={"kind": rng.choice(["fuerza", "fuego", "fuerza"])})
    group = client.get(f"/api/groups/{code}", headers=auth(names[0])).json()
    members = {m["display_name"]: m["user_id"] for m in group["members"]}
    catalog = client.get("/api/exercises", headers=auth(names[0])).json()
    bench = next(e["id"] for e in catalog if e["name"] == "Press banca")
    duel = client.post(f"/api/groups/{code}/duels", headers=auth("Nacho"),
                       json={"opponent_id": members["Bruno"], "exercise_id": bench, "mode": "dots", "days": 7})
    if duel.status_code == 201:
        client.post(f"/api/groups/{code}/duels/{duel.json()['id']}/accept", headers=auth("Bruno"))
    client.post(f"/api/groups/{code}/duels", headers=auth("Lucía"),
                json={"opponent_id": members["Flor"], "exercise_id": bench, "mode": "absolute", "days": 14})


def main() -> None:
    if config.AUTH_MODE != "dev":
        raise SystemExit("El seed solo corre en modo dev (sin AUTH0_DOMAIN).")
    parser = argparse.ArgumentParser(description="Puebla un grupo existente con participantes de mentira.")
    parser.add_argument("code", help="código del grupo")
    parser.add_argument("--as", dest="reader", required=True, help="nombre dev de un miembro del grupo")
    args = parser.parse_args()
    seed(args.code.upper(), args.reader)


if __name__ == "__main__":
    main()
