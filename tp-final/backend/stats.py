from dataclasses import dataclass
from datetime import date

# Más allá de 10 repeticiones la fórmula de Epley deja de ser confiable.
MAX_REPS_FOR_1RM = 10


@dataclass(frozen=True)
class SetRecord:
    member: str
    exercise: str
    date: date
    weight_kg: float
    reps: int


@dataclass(frozen=True)
class StrengthEntry:
    member: str
    best_1rm: float | None
    ratio: float | None


def estimate_1rm(weight_kg: float, reps: int) -> float | None:
    if reps > MAX_REPS_FOR_1RM:
        return None
    if reps == 1:
        return weight_kg
    return weight_kg * (1 + reps / 30)


def best_1rm_by_member(sets: list[SetRecord], exercise: str) -> dict[str, float]:
    best: dict[str, float] = {}
    for s in sets:
        if s.exercise != exercise:
            continue
        value = estimate_1rm(s.weight_kg, s.reps)
        if value is not None and value > best.get(s.member, 0):
            best[s.member] = value
    return best


def strength_ranking(
    sets: list[SetRecord],
    bodyweights: dict[str, float],
    challenges: list[str],
) -> dict[str, list[StrengthEntry]]:
    ranking = {}
    for exercise in challenges:
        best = best_1rm_by_member(sets, exercise)
        with_data = [StrengthEntry(m, best[m], best[m] / bodyweights[m]) for m in best if m in bodyweights]
        with_data.sort(key=lambda e: e.ratio, reverse=True)
        without_data = [StrengthEntry(m, None, None) for m in sorted(bodyweights) if m not in best]
        ranking[exercise] = with_data + without_data
    return ranking
