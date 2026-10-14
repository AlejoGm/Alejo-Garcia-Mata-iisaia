"""Puebla un grupo que ya existe con participantes de mentira, campañas y duelos. Solo en modo dev.

    uv run python -m scripts.seed_group CODIGO --as alejo [--weeks 26] [--me]

`--as` es el nombre (dev) de un miembro del grupo; si es admin, también crea campañas. Los participantes siguen
la primera rutina del grupo y entrenan sus días en orden; sin rutina, hacen los desafíos. Se puede correr de
nuevo: los que ya están no se vuelven a sumar y no se cargan sesiones en días que ya entrenaron. Con `--me`, el
que corre el script también recibe historia, con su peso y su objetivo, sin tocarle el perfil.
"""
import argparse
import random
from datetime import date, timedelta
from urllib.parse import quote

from fastapi.testclient import TestClient
from sqlmodel import Session

from backend import config
from backend.db import engine
from backend.main import app
from backend.models import Duel

# nombre, peso corporal, objetivo semanal, factor de fuerza, probabilidad de saltearse una semana, semanas que lleva
FAKES = [
    ("Nacho", 84, 4, 1.15, 0.05, 26),
    ("Tomi", 74, 4, 0.95, 0.10, 26),
    ("Bruno", 92, 5, 1.25, 0.04, 26),
    ("Facu", 79, 3, 1.00, 0.20, 26),
    ("Juani", 70, 4, 0.85, 0.08, 18),
    ("Pipe", 98, 3, 1.30, 0.25, 26),
    ("Lauti", 76, 5, 1.05, 0.06, 12),
    ("Santi", 88, 4, 1.10, 0.12, 22),
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


def strength(elapsed: float, week: int) -> float:
    """Sube un 20 % a lo largo de la historia, con una semana de descarga cada 8."""
    return (0.82 + 0.2 * elapsed) * (0.9 if week % 8 == 7 else 1.0)


def training_days(rng: random.Random, goal: int, monday: date, today: date) -> list[date]:
    count = max(1, min(6, goal + rng.choice([-1, 0, 0, 0, 1])))
    days = sorted(rng.sample(range(6), count))
    return [monday + timedelta(days=d) for d in days if monday + timedelta(days=d) <= today]


def session_sets(rng: random.Random, plan: list[tuple[dict, int]], factor: float, level: float) -> list[dict]:
    sets = []
    for exercise, count in plan:
        top = base_weight(exercise) * factor * level * rng.uniform(0.95, 1.05)
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


def seed_person(client: TestClient, code: str, fake: tuple, position: int, plans: tuple, weeks: int,
                profile: bool = True) -> int:
    name, bodyweight, goal, factor, skip, history = fake
    plan_days, day_ids, routine_id = plans
    rng = random.Random(f"{code}-{name}")
    headers = auth(name)
    if profile:
        client.put("/api/me", headers=headers, json={"display_name": name, "sex": "M", "weekly_goal": goal})
        client.post(f"/api/groups/{code}/join", headers=headers)
    if routine_id:
        client.put(f"/api/groups/{code}/members/me/routine", headers=headers, json={"routine_id": routine_id})
    trained = {d["day"] for d in client.get("/api/me/stats", headers=headers).json()["calendar"]}
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    span = min(weeks, history)
    day_index, added = position, 0  # cada uno arranca la rutina en un día distinto
    for week in range(span - 1, -1, -1):
        if week and rng.random() < skip:
            continue  # vacaciones, laburo, una gripe
        level = strength((span - 1 - week) / max(span - 1, 1), span - 1 - week)
        for day in training_days(rng, goal, this_monday - timedelta(weeks=week), today):
            slot = day_index % len(plan_days)
            day_index += 1
            # Se arma igual aunque el día ya esté cargado: así el azar no se desfasa y repetir no agrega días nuevos.
            body = {"date": day.isoformat(), "bodyweight_kg": round(bodyweight + rng.uniform(-1.2, 1.2), 1),
                    "routine_day_id": day_ids[slot], "sets": session_sets(rng, plan_days[slot], factor, level)}
            if day.isoformat() not in trained:
                client.post("/api/me/sessions", headers=headers, json=body)
                added += 1
    return added


def react(client: TestClient, code: str, rng: random.Random) -> None:
    names = [f[0] for f in FAKES]
    for item in client.get(f"/api/groups/{code}/feed?limit=80", headers=auth(names[0])).json():
        for name in rng.sample(names, 3):
            if name.lower() != item["display_name"].lower():
                client.put(f"/api/groups/{code}/feed/{item['set_id']}/reaction", headers=auth(name),
                           json={"kind": rng.choice(["fuerza", "fuego", "fuerza", "fuego", "fuerza"])})


def duels(client: TestClient, code: str, catalog: dict[str, int], members: dict[str, int]) -> None:
    """Duelos terminados, en curso y pendientes. La API arranca un duelo al aceptarlo, así que se corre la fecha."""
    plan = [  # retador, retado, ejercicio, modo, días, hace cuántos días arrancó (None: queda pendiente)
        ("Nacho", "Bruno", "Press banca", "dots", 14, 40), ("Tomi", "Facu", "Sentadilla", "absolute", 7, 25),
        ("Santi", "Pipe", "Press banca", "absolute", 14, 18), ("Juani", "Lauti", "Sentadilla", "dots", 7, 3),
        ("Bruno", "Santi", "Sentadilla", "dots", 14, 5), ("Facu", "Nacho", "Press banca", "dots", 7, None),
    ]
    for challenger, opponent, exercise, mode, days, ago in plan:
        if challenger not in members or opponent not in members:
            continue
        created = client.post(f"/api/groups/{code}/duels", headers=auth(challenger), json={
            "opponent_id": members[opponent], "exercise_id": catalog[exercise], "mode": mode, "days": days})
        if created.status_code != 201 or ago is None:
            continue
        client.post(f"/api/groups/{code}/duels/{created.json()['id']}/accept", headers=auth(opponent))
        with Session(engine) as session:
            duel = session.get(Duel, created.json()["id"])
            duel.start = date.today() - timedelta(days=ago)
            session.commit()


def campaigns(client: TestClient, code: str, reader: dict, catalog: dict[str, int]) -> int:
    """Dos campañas cerradas (con ganador) y la del mes, si el grupo no tiene ninguna."""
    if client.get(f"/api/groups/{code}/campaigns", headers=reader).json():
        return 0
    today = date.today()
    month = today.replace(day=1)
    month_end = (month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    tables = [f"dots:{catalog['Sentadilla']}", f"dots:{catalog['Press banca']}", f"absolute:{catalog['Press banca']}",
              "progress", "consistency"]
    created = 0
    for name, start, end in [("Invierno", today - timedelta(weeks=20), today - timedelta(weeks=13)),
                             ("Primavera", today - timedelta(weeks=10), today - timedelta(weeks=3)),
                             (f"Copa {month.strftime('%m/%Y')}", month, month_end)]:
        response = client.post(f"/api/groups/{code}/campaigns", headers=reader, json={
            "name": name, "start": start.isoformat(), "end": end.isoformat(), "tables": tables})
        created += response.status_code == 201
    client.get(f"/api/groups/{code}/campaigns", headers=reader)  # leerlas congela el ganador de las cerradas
    return created


def seed(code: str, reader_name: str, weeks: int, me: bool) -> None:
    reader = auth(reader_name)
    with TestClient(app) as client:
        group = client.get(f"/api/groups/{code}", headers=reader)
        if group.status_code != 200:
            raise SystemExit(f"No se pudo leer el grupo {code} como '{reader_name}': {group.json().get('detail')}")
        group = group.json()
        plans = plans_for(client, code, reader, group)
        sessions = sum(seed_person(client, code, fake, i, plans, weeks) for i, fake in enumerate(FAKES))
        if me:
            profile = client.get("/api/me", headers=reader).json()
            mine = (reader_name, profile["last_bodyweight_kg"] or 80, profile["weekly_goal"] or 4, 1.05, 0.08, weeks)
            sessions += seed_person(client, code, mine, len(FAKES), plans, weeks, profile=False)
        react(client, code, random.Random(code))
        catalog = {e["name"]: e["id"] for e in client.get("/api/exercises", headers=reader).json()}
        detail = client.get(f"/api/groups/{code}", headers=reader).json()
        duels(client, code, catalog, {m["display_name"]: m["user_id"] for m in detail["members"]})
        made = campaigns(client, code, reader, catalog) if group["is_admin"] else 0
        print(f"Listo: {len(FAKES)} participantes en {group['name']} ({code}), {sessions} sesiones nuevas, "
              f"{made} campañas nuevas.")


def main() -> None:
    if config.AUTH_MODE == "auth0":
        raise SystemExit("El seed no corre con Auth0 configurado: renombrá el .env.")
    config.AUTH_MODE = "dev"  # el seed carga los datos en este proceso, entrando con nombres
    parser = argparse.ArgumentParser(description="Puebla un grupo existente con participantes de mentira.")
    parser.add_argument("code", help="código del grupo")
    parser.add_argument("--as", dest="reader", required=True, help="nombre dev de un miembro del grupo")
    parser.add_argument("--weeks", type=int, default=26, help="semanas de historia (por defecto 26)")
    parser.add_argument("--me", action="store_true", help="cargarle historia también al que corre el script")
    args = parser.parse_args()
    seed(args.code.upper(), args.reader, args.weeks, args.me)


if __name__ == "__main__":
    main()
