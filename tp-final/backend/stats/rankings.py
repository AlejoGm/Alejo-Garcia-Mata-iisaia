"""Tablas de fuerza, progreso, semana y constancia."""
from dataclasses import dataclass
from datetime import date, timedelta

from backend.stats.core import SetRecord, absolute_key, best_absolute, set_dots
from backend.stats.periods import by_user, in_range, month_start, shift_months


# Fuerza

@dataclass(frozen=True)
class StrengthEntry:
    user_id: int
    value: float | None
    weight_kg: float | None = None
    reps: int | None = None
    day: date | None = None


def strength_table(records: list[SetRecord], sexes: dict[int, str], exercise_id: int,
                   mode: str) -> list[StrengthEntry]:
    """Mejor marca de cada miembro en un ejercicio: DOTS del 1RM estimado, o absoluto. Sin datos al final."""
    grouped = by_user([r for r in records if r.exercise_id == exercise_id])
    rated: list[tuple[tuple, StrengthEntry]] = []
    missing = []
    for user_id, sex in sexes.items():
        mine = grouped.get(user_id, [])
        if mode == "dots":
            scored = [(set_dots(r, sex), r) for r in mine if r.estimated_1rm is not None]
            best = max(scored, key=lambda pair: (pair[0], -pair[1].date.toordinal()), default=None)
            if best:
                value, r = best
                rated.append(((value,), StrengthEntry(user_id, value, r.weight_kg, r.reps, r.date)))
                continue
        else:
            r = best_absolute(mine)
            if r:
                rated.append((absolute_key(r), StrengthEntry(user_id, r.load, r.weight_kg, r.reps, r.date)))
                continue
        missing.append(StrengthEntry(user_id, None))
    rated.sort(key=lambda pair: pair[0], reverse=True)
    return [entry for _, entry in rated] + sorted(missing, key=lambda e: e.user_id)


# Progreso

@dataclass(frozen=True)
class ProgressEntry:
    user_id: int
    pct: float | None
    exercises: int = 0


def best_1rm_by_exercise(records: list[SetRecord]) -> dict[int, float]:
    best: dict[int, float] = {}
    for record in records:
        value = record.estimated_1rm
        if value is not None and value > best.get(record.exercise_id, 0):
            best[record.exercise_id] = value
    return best


def progress_table(records: list[SetRecord], user_ids: list[int], current: tuple[date, date],
                   baseline: tuple[date, date]) -> list[ProgressEntry]:
    grouped = by_user(records)
    entries = []
    for user_id in user_ids:
        mine = grouped.get(user_id, [])
        now = best_1rm_by_exercise(in_range(mine, *current))
        before = best_1rm_by_exercise(in_range(mine, *baseline))
        common = [e for e in now if e in before]
        changes = [100 * (now[e] / before[e] - 1) for e in common]
        entries.append(ProgressEntry(user_id, sum(changes) / len(changes) if changes else None, len(changes)))
    return sorted(entries, key=lambda e: (e.pct is None, -(e.pct or 0), e.user_id))


def progress_windows(start: date, end: date) -> tuple[tuple[date, date], tuple[date, date]]:
    """El último mes del período contra el mes anterior a que empiece."""
    return (month_start(end), end), (shift_months(start, -1), start - timedelta(days=1))


# Semana y constancia

def monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


def goal_in_force(changes: list[tuple[date, int]], week: date) -> int | None:
    current = None
    for start, goal in sorted(changes):
        if start <= week:
            current = goal
    return current


def training_days(records: list[SetRecord]) -> set[date]:
    return {r.date for r in records}


@dataclass(frozen=True)
class WeeklyEntry:
    user_id: int
    sessions: int
    goal: int | None
    status: str  # "done", "on" o "out"


def weekly_table(records: list[SetRecord], goals: dict[int, int | None], today: date) -> list[WeeklyEntry]:
    start = monday(today)
    grouped = by_user(in_range(records, start, start + timedelta(days=6)))
    entries = []
    for user_id, goal in goals.items():
        days = training_days(grouped.get(user_id, []))
        sessions = len(days)
        # Quedan los días después de hoy, más hoy si todavía no entrenó.
        free_days = 6 - today.weekday() + (0 if today in days else 1)
        if goal and sessions >= goal:
            status = "done"
        elif goal and goal - sessions > free_days:
            status = "out"
        else:
            status = "on"
        entries.append(WeeklyEntry(user_id, sessions, goal, status))
    return sorted(entries, key=lambda e: (-e.sessions, -(e.sessions / e.goal if e.goal else 0), e.user_id))


@dataclass(frozen=True)
class ConsistencyEntry:
    user_id: int
    pct: float | None
    streak: int = 0
    weeks: int = 0


def week_results(days: set[date], changes: list[tuple[date, int]], today: date) -> dict[date, bool]:
    """Para cada semana cerrada desde la primera sesión: si se llegó al objetivo vigente."""
    if not days:
        return {}
    results = {}
    week = monday(min(days))
    this_week = monday(today)
    while week < this_week:
        goal = goal_in_force(changes, week)
        if goal:
            count = sum(1 for d in days if week <= d <= week + timedelta(days=6))
            results[week] = count >= goal
        week += timedelta(days=7)
    return results


def consistency_table(records: list[SetRecord], goals: dict[int, list[tuple[date, int]]], start: date,
                      end: date, today: date) -> list[ConsistencyEntry]:
    grouped = by_user(records)
    entries = []
    for user_id, changes in goals.items():
        results = week_results(training_days(grouped.get(user_id, [])), changes, today)
        in_period = [met for week, met in results.items() if week >= monday(start) and week <= end]
        streak = 0
        for week in sorted(results, reverse=True):
            if not results[week]:
                break
            streak += 1
        pct = 100 * sum(in_period) / len(in_period) if in_period else None
        entries.append(ConsistencyEntry(user_id, pct, streak, len(in_period)))
    return sorted(entries, key=lambda e: (e.pct is None, -(e.pct or 0), -e.streak, e.user_id))
