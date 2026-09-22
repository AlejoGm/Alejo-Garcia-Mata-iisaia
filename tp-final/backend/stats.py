from dataclasses import dataclass
from datetime import date


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
    raise NotImplementedError


def strength_ranking(
    sets: list[SetRecord],
    bodyweights: dict[str, float],
    challenges: list[str],
) -> dict[str, list[StrengthEntry]]:
    raise NotImplementedError
