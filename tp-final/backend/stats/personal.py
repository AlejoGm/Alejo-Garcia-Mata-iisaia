"""Series para los gráficos personales."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from backend.stats.core import SetRecord, chronological_key
from backend.stats.periods import in_range, month_start, shift_months
from backend.stats.rankings import monday


@dataclass(frozen=True)
class MonthPoint:
    month: date
    best: float | None
    average: float | None


@dataclass(frozen=True)
class WeekPoint:
    week: date
    best: float | None


@dataclass(frozen=True)
class BodyweightPoint:
    week: date
    kg: float


def r1(value: float | None) -> float | None:
    return None if value is None else round(value, 1)


def session_bests(records: list[SetRecord]) -> dict[int, tuple[date, float]]:
    """Mejor 1RM estimado de cada sesión: (fecha, valor)."""
    best: dict[int, tuple[date, float]] = {}
    for r in records:
        value = r.estimated_1rm
        if value is not None and value > best.get(r.session_id, (r.date, 0))[1]:
            best[r.session_id] = (r.date, value)
    return best


def monthly_series(records: list[SetRecord], exercise_id: int, start: date, end: date) -> list[MonthPoint]:
    mine = [r for r in in_range(records, start, end) if r.exercise_id == exercise_id]
    by_month: dict[date, list[float]] = defaultdict(list)
    for day, value in session_bests(mine).values():
        by_month[month_start(day)].append(value)
    points = []
    month = month_start(start)
    while month <= end:
        values = by_month.get(month, [])
        points.append(MonthPoint(month, r1(max(values)) if values else None,
                                 r1(sum(values) / len(values)) if values else None))
        month = shift_months(month, 1)
    return points


def weekly_series(records: list[SetRecord], exercise_id: int, start: date, end: date) -> list[WeekPoint]:
    mine = [r for r in in_range(records, start, end) if r.exercise_id == exercise_id]
    by_week: dict[date, float] = {}
    for day, value in session_bests(mine).values():
        week = monday(day)
        by_week[week] = max(by_week.get(week, 0), value)
    return [WeekPoint(week, r1(value)) for week, value in sorted(by_week.items())]


def bodyweight_series(records: list[SetRecord], start: date, end: date) -> list[BodyweightPoint]:
    last: dict[date, SetRecord] = {}
    for r in sorted(in_range(records, start, end), key=chronological_key):
        last[monday(r.date)] = r
    return [BodyweightPoint(week, r.bodyweight_kg) for week, r in sorted(last.items())]
