"""Cuentas del panel del grupo."""
from dataclasses import dataclass
from datetime import date, timedelta

from backend.stats.core import SetRecord
from backend.stats.periods import by_user, in_range
from backend.stats.rankings import monday, training_days


@dataclass(frozen=True)
class WeekActivity:
    week: date
    sessions: int
    volume: float


@dataclass(frozen=True)
class DayActivity:
    day: date
    members: int


def volume(records: list[SetRecord]) -> float:
    return sum(r.load * r.reps for r in records)


def session_count(records: list[SetRecord]) -> int:
    return len({(r.user_id, r.date) for r in records})


def weekly_activity(records: list[SetRecord], today: date, weeks: int = 8) -> list[WeekActivity]:
    """Sesiones y volumen de las últimas `weeks` semanas, de la más vieja a la actual."""
    this_week = monday(today)
    series = []
    for offset in range(weeks - 1, -1, -1):
        start = this_week - timedelta(days=7 * offset)
        window = in_range(records, start, start + timedelta(days=6))
        series.append(WeekActivity(start, session_count(window), volume(window)))
    return series


def day_activity(records: list[SetRecord], today: date) -> list[DayActivity]:
    start = monday(today)
    days = []
    for offset in range(7):
        day = start + timedelta(days=offset)
        days.append(DayActivity(day, len({r.user_id for r in records if r.date == day})))
    return days


def goal_progress(records: list[SetRecord], goals: dict[int, int | None], today: date) -> float | None:
    """Sesiones de la semana topeadas en el objetivo de cada uno, sobre la suma de los objetivos."""
    start = monday(today)
    grouped = by_user(in_range(records, start, start + timedelta(days=6)))
    with_goal = {uid: goal for uid, goal in goals.items() if goal}
    if not with_goal:
        return None
    done = sum(min(len(training_days(grouped.get(uid, []))), goal) for uid, goal in with_goal.items())
    return 100 * done / sum(with_goal.values())
