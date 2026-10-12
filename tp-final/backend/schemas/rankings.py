from datetime import date
from typing import Literal

from pydantic import BaseModel

from backend.schemas.common import PeriodOut


class StrengthRow(BaseModel):
    user_id: int
    display_name: str
    value: float | None
    weight_kg: float | None
    reps: int | None


class StrengthExercise(BaseModel):
    exercise_id: int
    exercise: str
    dots: list[StrengthRow]
    absolute: list[StrengthRow]


class ProgressRow(BaseModel):
    user_id: int
    display_name: str
    pct: float | None
    exercises: int


class WeeklyRow(BaseModel):
    user_id: int
    display_name: str
    sessions: int
    goal: int | None
    status: str


class ConsistencyRow(BaseModel):
    user_id: int
    display_name: str
    pct: float | None
    streak: int
    weeks: int


class RankingsOut(BaseModel):
    period: PeriodOut
    strength: list[StrengthExercise]
    progress: list[ProgressRow]
    weekly: list[WeeklyRow]
    consistency: list[ConsistencyRow]


ReactionKind = Literal["fuerza", "fuego", "dudoso"]


class ReactionInput(BaseModel):
    kind: ReactionKind


class FeedItem(BaseModel):
    set_id: int
    user_id: int
    display_name: str
    exercise: str
    date: date
    weight_kg: float
    reps: int
    load: float
    estimated_1rm: float | None
    pr: str
    reactions: dict[str, int]
    mine: str | None
    excluded: bool
