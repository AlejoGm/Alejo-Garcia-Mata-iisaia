from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SetRecord:
    set_id: int
    session_id: int
    user_id: int
    exercise_id: int
    date: date
    weight_kg: float
    reps: int
    bodyweight_kg: float
    bodyweight_exercise: bool = False
    position: int = 0

    @property
    def load(self) -> float:
        raise NotImplementedError


def estimate_1rm(load: float, reps: int) -> float | None:
    raise NotImplementedError


def dots(lifted: float, bodyweight: float, sex: str) -> float:
    raise NotImplementedError


def best_absolute(records: list[SetRecord]) -> SetRecord | None:
    raise NotImplementedError


def detect_prs(records: list[SetRecord]) -> dict[int, str]:
    raise NotImplementedError
