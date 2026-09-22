from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator


class GroupInput(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]


class GroupOut(BaseModel):
    code: str
    name: str


class MemberInput(BaseModel):
    nickname: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
    bodyweight_kg: Annotated[float, Field(gt=0, le=300)]


class MemberOut(BaseModel):
    nickname: str
    bodyweight_kg: float


class ExerciseOut(BaseModel):
    id: int
    name: str
    is_challenge: bool


class GroupDetail(GroupOut):
    members: list[MemberOut]
    exercises: list[ExerciseOut]


class SetInput(BaseModel):
    exercise_id: int
    weight_kg: Annotated[float, Field(gt=0, le=500)]
    reps: Annotated[int, Field(ge=1, le=50)]


class SessionInput(BaseModel):
    date: date
    sets: Annotated[list[SetInput], Field(min_length=1)]

    @field_validator("date")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("La fecha no puede ser futura")
        return value


class SetOut(BaseModel):
    exercise_id: int
    exercise: str
    weight_kg: float
    reps: int
    estimated_1rm: float | None


class SessionOut(BaseModel):
    id: int
    date: date
    sets: list[SetOut]


class StrengthEntryOut(BaseModel):
    nickname: str
    best_1rm: float | None
    ratio: float | None


class StrengthRankingOut(BaseModel):
    exercise: str
    entries: list[StrengthEntryOut]


class RankingsOut(BaseModel):
    strength: list[StrengthRankingOut]
