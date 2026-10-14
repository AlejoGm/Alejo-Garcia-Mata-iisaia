from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from backend.schemas.common import Person


class SetInput(BaseModel):
    exercise_id: int
    weight_kg: Annotated[float, Field(ge=0, le=500)]
    reps: Annotated[int, Field(ge=1, le=50)]


class SessionInput(BaseModel):
    date: date
    bodyweight_kg: Annotated[float, Field(ge=30, le=300)]
    routine_day_id: int | None = None
    sets: Annotated[list[SetInput], Field(min_length=1, max_length=100)]

    @field_validator("date")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("La fecha no puede ser futura")
        return value


class SetOut(BaseModel):
    id: int
    exercise_id: int
    exercise: str
    weight_kg: float
    reps: int
    load: float
    estimated_1rm: float | None
    dots: float | None
    pr: str | None


class SessionOut(BaseModel):
    id: int
    date: date
    bodyweight_kg: float
    routine_day_id: int | None
    routine_day_name: str | None = None
    sets: list[SetOut]


class LastSet(BaseModel):
    display_name: str
    weight_kg: float
    reps: int
    date: date


class TargetOut(BaseModel):
    kind: str
    weight_kg: float
    reps: int


class LastOut(BaseModel):
    mine: LastSet | None
    others: list[LastSet]
    targets: list[TargetOut]


class StandingInput(BaseModel):
    exercise_id: int
    weight_kg: Annotated[float, Field(ge=0, le=500)]
    reps: Annotated[int, Field(ge=1, le=50)]
    bodyweight_kg: Annotated[float, Field(ge=30, le=300)]


class NextRivalOut(BaseModel):
    user_id: int
    display_name: str
    dots: float
    weight_kg: float | None
    reps: int


class StandingOut(BaseModel):
    pr: str | None
    estimated_1rm: float | None
    dots: float | None
    position_before: int | None
    position: int | None
    total: int
    passed: list[Person]
    next: NextRivalOut | None
