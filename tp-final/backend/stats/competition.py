"""Duelos, campañas y cara a cara."""
from dataclasses import dataclass
from datetime import date, timedelta

from backend.stats.core import SetRecord, best_1rm, best_absolute, set_dots
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


# Cara a cara

@dataclass(frozen=True)
class FaceOff:
    exercise_id: int
    mine_1rm: float
    theirs_1rm: float
    mine_dots: float
    theirs_dots: float
    winner: str  # "mine", "theirs" o "tie"


def by_exercise(records: list[SetRecord]) -> dict[int, list[SetRecord]]:
    grouped: dict[int, list[SetRecord]] = {}
    for record in records:
        grouped.setdefault(record.exercise_id, []).append(record)
    return grouped


def head_to_head(mine: list[SetRecord], theirs: list[SetRecord], my_sex: str, their_sex: str) -> list[FaceOff]:
    """Por cada ejercicio con 1RM estimable en los dos: mejor 1RM de cada uno y quién gana en DOTS."""
    a, b = by_exercise(mine), by_exercise(theirs)
    result = []
    for exercise_id in sorted(set(a) & set(b)):
        a_rm, b_rm = best_1rm(a[exercise_id]), best_1rm(b[exercise_id])
        if a_rm is None or b_rm is None:
            continue
        a_dots = best_value(a[exercise_id], my_sex, "dots")[0]
        b_dots = best_value(b[exercise_id], their_sex, "dots")[0]
        winner = "tie" if a_dots == b_dots else "mine" if a_dots > b_dots else "theirs"
        result.append(FaceOff(exercise_id, a_rm.estimated_1rm, b_rm.estimated_1rm, a_dots, b_dots, winner))
    return result
