"""Líneas para comparar a los miembros en el panel: fuerza por mes y días por semana."""
from datetime import date, timedelta

from backend.stats.core import SetRecord, set_dots
from backend.stats.periods import in_range, month_start, shift_months
from backend.stats.rankings import monday


def month_list(start: date, end: date) -> list[date]:
    months, month = [], month_start(start)
    while month <= end:
        months.append(month)
        month = shift_months(month, 1)
    return months


def monthly_best_by_user(records: list[SetRecord], exercise_id: int, start: date, end: date, sexes: dict[int, str],
                         metric: str) -> dict[int, list[float | None]]:
    """Por miembro, el mejor 1RM estimado (o su DOTS) de cada mes del período. None si ese mes no hay dato."""
    months = month_list(start, end)
    index = {m: i for i, m in enumerate(months)}
    lines: dict[int, list[float | None]] = {uid: [None] * len(months) for uid in sexes}
    for r in in_range(records, start, end):
        if r.exercise_id != exercise_id or r.user_id not in lines or r.estimated_1rm is None:
            continue
        value = r.estimated_1rm if metric == "1rm" else set_dots(r, sexes[r.user_id])
        slot = index[month_start(r.date)]
        current = lines[r.user_id][slot]
        lines[r.user_id][slot] = value if current is None else max(current, value)
    return {uid: [None if v is None else round(v, 1) for v in values] for uid, values in lines.items()}


def weekly_days_by_user(records: list[SetRecord], user_ids: list[int], today: date,
                        weeks: int = 12) -> tuple[list[date], dict[int, list[int]]]:
    """Las últimas `weeks` semanas (de la más vieja a la actual) y los días entrenados de cada miembro en cada una."""
    this_week = monday(today)
    starts = [this_week - timedelta(weeks=offset) for offset in range(weeks - 1, -1, -1)]
    index = {w: i for i, w in enumerate(starts)}
    days: dict[int, set] = {uid: set() for uid in user_ids}
    for r in in_range(records, starts[0], today):
        if r.user_id in days:
            days[r.user_id].add(r.date)
    counts = {uid: [0] * weeks for uid in user_ids}
    for uid, trained in days.items():
        for day in trained:
            counts[uid][index[monday(day)]] += 1
    return starts, counts
