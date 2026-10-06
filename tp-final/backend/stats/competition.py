"""Duelos y campañas."""
from dataclasses import dataclass
from datetime import date, timedelta

from backend.stats.core import SetRecord, best_absolute, set_dots
from backend.stats.periods import by_user, in_range


# Duelos

@dataclass(frozen=True)
class DuelResult:
    challenger_value: float | None
    opponent_value: float | None
    winner: int | None
    finished: bool
    end: date


def best_value(records: list[SetRecord], sex: str, mode: str) -> tuple | None:
    """Valor comparable de la mejor serie: (dots,) o (carga, reps)."""
    if mode == "dots":
        values = [set_dots(r, sex) for r in records if r.estimated_1rm is not None]
        return (max(values),) if values else None
    best = best_absolute(records)
    return (best.load, best.reps) if best else None


def duel_result(records: list[SetRecord], sexes: dict[int, str], challenger: int, opponent: int, exercise_id: int,
                mode: str, start: date, days: int, today: date) -> DuelResult:
    end = start + timedelta(days=days - 1)
    window = [r for r in in_range(records, start, end) if r.exercise_id == exercise_id]
    grouped = by_user(window)
    a = best_value(grouped.get(challenger, []), sexes[challenger], mode)
    b = best_value(grouped.get(opponent, []), sexes[opponent], mode)
    if a is None and b is None or a == b:
        winner = None
    elif b is None or (a is not None and a > b):
        winner = challenger
    else:
        winner = opponent
    return DuelResult(a[0] if a else None, b[0] if b else None, winner, today > end, end)


def imbalance(a: float | None, b: float | None) -> tuple[str, float | None]:
    if not a or not b:
        return "none", None
    ratio = round(abs(a - b) / max(a, b), 4)
    if ratio <= 0.10:
        return "low", ratio
    if ratio <= 0.25:
        return "medium", ratio
    return "high", ratio


# Campañas

CAMPAIGN_POINTS = [10, 8, 6, 5, 4, 3, 2, 1]


@dataclass(frozen=True)
class CampaignEntry:
    user_id: int
    points: int
    firsts: int


def campaign_points(tables: list[list[int]], user_ids: list[int]) -> list[CampaignEntry]:
    """Cada tabla es la lista de usuarios con datos, del primero al último. Sin datos no suma."""
    points = {uid: 0 for uid in user_ids}
    firsts = {uid: 0 for uid in user_ids}
    for table in tables:
        for position, uid in enumerate(table[:len(CAMPAIGN_POINTS)]):
            if uid in points:
                points[uid] += CAMPAIGN_POINTS[position]
                firsts[uid] += position == 0
    order = {uid: index for index, uid in enumerate(user_ids)}
    entries = [CampaignEntry(uid, points[uid], firsts[uid]) for uid in user_ids]
    return sorted(entries, key=lambda e: (-e.points, -e.firsts, order[e.user_id]))
