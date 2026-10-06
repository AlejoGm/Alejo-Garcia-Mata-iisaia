"""Carga un grupo de demo con 8 semanas de historia. Solo en modo dev: usa tokens `dev:<nombre>`.

    uv run python -m scripts.seed_demo

Imprime el código del grupo. Para volver a empezar, borrar gymbro.db.
"""
import random
from datetime import date, timedelta

from fastapi.testclient import TestClient

from backend import config
from backend.main import app

PEOPLE = [  # nombre, sexo, peso, objetivo, cargas base de sentadilla/banca/peso muerto/militar
    ("Gustavo", "M", 95, 4, (150, 105, 180, 62)),
    ("Mati", "M", 72, 3, (120, 85, 150, 50)),
    ("Caro", "F", 61, 3, (80, 47, 100, 32)),
]
ROUTINE = {"name": "Push/Pull/Legs", "days": [
    {"name": "Push", "items": [["Press banca", 4], ["Press militar", 3], ["Fondos", 3]]},
    {"name": "Pull", "items": [["Dominadas", 4], ["Remo con barra", 3], ["Curl de bíceps", 3]]},
    {"name": "Legs", "items": [["Sentadilla", 4], ["Peso muerto rumano", 3], ["Elevación de talones", 3]]},
]}


def auth(name: str) -> dict:
    return {"Authorization": f"Bearer dev:{name.lower()}"}


def main() -> None:
    if config.AUTH_MODE != "dev":
        raise SystemExit("El seed solo corre en modo dev (sin AUTH0_DOMAIN).")
    rng = random.Random(7)
    with TestClient(app) as client:
        for name, sex, _bw, goal, _ in PEOPLE:
            client.put("/api/me", headers=auth(name), json={"display_name": name, "sex": sex, "weekly_goal": goal})
        ids = {e["name"]: e["id"] for e in client.get("/api/exercises", headers=auth("Gustavo")).json()}
        code = client.post("/api/groups", headers=auth("Gustavo"), json={"name": "Los del gym"}).json()["code"]
        for name, *_ in PEOPLE[1:]:
            client.post(f"/api/groups/{code}/join", headers=auth(name))
        routine_body = {"name": ROUTINE["name"], "days": [
            {"name": d["name"], "items": [{"exercise_id": ids[e], "sets": s} for e, s in d["items"]]} for d in ROUTINE["days"]]}
        routine = client.post(f"/api/groups/{code}/routines", headers=auth("Gustavo"), json=routine_body).json()
        for name, *_ in PEOPLE[:2]:
            client.put(f"/api/groups/{code}/members/me/routine", headers=auth(name), json={"routine_id": routine["id"]})

        lifts = ["Sentadilla", "Press banca", "Peso muerto", "Press militar"]
        today = date.today()
        for name, _sex, bw, goal, base in PEOPLE:
            for week in range(8, 0, -1):
                monday = today - timedelta(days=today.weekday() + 7 * week)
                for day in sorted(rng.sample(range(6), goal if rng.random() > 0.2 else goal - 1)):
                    progress = 1 + (8 - week) * 0.012
                    lift = lifts[day % 4]
                    top = round(base[lifts.index(lift)] * progress / 2.5) * 2.5
                    sets = [{"exercise_id": ids[lift], "weight_kg": top - 10, "reps": 8},
                            {"exercise_id": ids[lift], "weight_kg": top, "reps": rng.choice([3, 4, 5])}]
                    # Accesorios de la rutina, para que "la última vez" tenga datos en todos los días.
                    for extra, kg in (("Dominadas", 0), ("Fondos", 0), ("Remo con barra", base[1] * 0.8)):
                        sets.append({"exercise_id": ids[extra], "weight_kg": round(kg * progress / 2.5) * 2.5,
                                     "reps": rng.choice([6, 8, 10])})
                    client.post("/api/me/sessions", headers=auth(name), json={
                        "date": (monday + timedelta(days=day)).isoformat(),
                        "bodyweight_kg": round(bw + rng.uniform(-0.8, 0.8), 1), "sets": sets})
        client.post(f"/api/groups/{code}/campaigns", headers=auth("Gustavo"), json={
            "name": "Octubre", "start": today.replace(day=1).isoformat(),
            "end": ((today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)).isoformat(),
            "tables": [f"dots:{ids['Sentadilla']}", f"dots:{ids['Press banca']}", "progress", "consistency"]})
        print(f"Grupo de demo: {code}")


if __name__ == "__main__":
    main()
