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


@dataclass(frozen=True)
class WeekAwards:
    week: date
    most_days: list[int]
    days: int
    most_volume: list[int]
    volume: float
    most_prs: list[int]
    prs: int
    goal_met: list[int]


def leaders_of(values: dict[int, float]) -> tuple[list[int], float]:
    """Todos los empatados en el máximo; nadie si el máximo es 0."""
    top = max(values.values(), default=0)
    return ([uid for uid, value in values.items() if value == top] if top else []), top


def week_awards(records: list[SetRecord], prs: set[int], goals: dict[int, int | None], week: date) -> WeekAwards:
    """Premios de una semana cerrada entre los usuarios de `goals`: días, volumen, PRs y objetivo cumplido."""
    grouped = by_user(in_range(records, week, week + timedelta(days=6)))
    mine = {uid: grouped.get(uid, []) for uid in goals}
    days = {uid: len(training_days(rs)) for uid, rs in mine.items()}
    most_days, top_days = leaders_of(days)
    most_volume, top_volume = leaders_of({uid: volume(rs) for uid, rs in mine.items()})
    most_prs, top_prs = leaders_of({uid: sum(1 for r in rs if r.set_id in prs) for uid, rs in mine.items()})
    met = [uid for uid, goal in goals.items() if goal and days[uid] >= goal]
    return WeekAwards(week, most_days, top_days, most_volume, top_volume, most_prs, top_prs, met)
