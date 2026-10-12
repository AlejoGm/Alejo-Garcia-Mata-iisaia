"""Medallas: hitos personales con el día en que se ganaron."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from backend.stats.core import SetRecord, chronological_key, detect_prs
from backend.stats.rankings import training_days, week_results

# clave: (título, descripción). El orden es el del catálogo de medallas.
ACHIEVEMENTS = {
    "first": ("Primera sesión", "Cargaste tu primera sesión."),
    "sessions_10": ("10 sesiones", "Diez días entrenados."),
    "sessions_50": ("50 sesiones", "Cincuenta días entrenados."),
    "sessions_100": ("100 sesiones", "Cien días entrenados."),
    "streak_4": ("4 semanas", "Cuatro semanas seguidas cumpliendo tu objetivo."),
    "streak_12": ("12 semanas", "Doce semanas seguidas cumpliendo tu objetivo."),
    "prs_10": ("10 PRs", "Rompiste diez marcas."),
    "bench_bw": ("Banca con tu peso", "Press banca con tu peso corporal o más."),
    "squat_1_5": ("Sentadilla 1,5×", "Sentadilla con una vez y media tu peso."),
    "deadlift_2": ("Peso muerto 2×", "Peso muerto con el doble de tu peso."),
    "ton": ("Tonelada", "10 000 kg de volumen en una sesión."),
}

# medalla: (levantamiento, veces el peso corporal)
STRENGTH = {"bench_bw": ("bench", 1.0), "squat_1_5": ("squat", 1.5), "deadlift_2": ("deadlift", 2.0)}
TON_KG = 10_000


@dataclass(frozen=True)
class Achievement:
    key: str
    day: date


def nth(items: list, n: int):
    return items[n - 1] if len(items) >= n else None


def streak_days(days: set[date], changes: list[tuple[date, int]], today: date) -> dict[int, date]:
    """Para cada largo de racha alcanzado, el domingo de la semana en que se alcanzó por primera vez."""
    reached: dict[int, date] = {}
    streak = 0
    for week, met in sorted(week_results(days, changes, today).items()):
        streak = streak + 1 if met else 0
        if streak and streak not in reached:
            reached[streak] = week + timedelta(days=6)
    return reached


def first_heavy_day(records: list[SetRecord], exercise_id: int | None, ratio: float) -> date | None:
    return next((r.date for r in records if r.exercise_id == exercise_id and r.load >= ratio * r.bodyweight_kg), None)


def first_ton_day(records: list[SetRecord]) -> date | None:
    volume: dict[tuple, float] = defaultdict(float)
    for r in records:
        volume[(r.date, r.session_id)] += r.load * r.reps
    return next((key[0] for key in sorted(volume) if volume[key] >= TON_KG), None)


def achievements(records: list[SetRecord], changes: list[tuple[date, int]], lifts: dict[str, int],
                 today: date) -> list[Achievement]:
    """Medallas de un usuario. `lifts` dice qué ejercicio es "bench", "squat" y "deadlift"."""
    ordered = sorted(records, key=chronological_key)
    days = sorted(training_days(ordered))
    prs = detect_prs(ordered)
    streaks = streak_days(set(days), changes, today)
    found = {
        "first": nth(days, 1),
        "sessions_10": nth(days, 10),
        "sessions_50": nth(days, 50),
        "sessions_100": nth(days, 100),
        "streak_4": streaks.get(4),
        "streak_12": streaks.get(12),
        "prs_10": nth([r.date for r in ordered if r.set_id in prs], 10),
        "ton": first_ton_day(ordered),
    }
    for key, (lift, ratio) in STRENGTH.items():
        found[key] = first_heavy_day(ordered, lifts.get(lift), ratio)
    return [Achievement(key, found[key]) for key in ACHIEVEMENTS if found[key] is not None]
