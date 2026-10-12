from typing import Annotated

from pydantic import BaseModel, Field

from backend.schemas.common import Name30, Name40


class RoutineItemInput(BaseModel):
    exercise_id: int
    sets: Annotated[int, Field(ge=1, le=10)]


class RoutineDayInput(BaseModel):
    name: Name30
    items: Annotated[list[RoutineItemInput], Field(min_length=1, max_length=12)]


class RoutineInput(BaseModel):
    name: Name40
    days: Annotated[list[RoutineDayInput], Field(min_length=1, max_length=7)]


class RoutineItemOut(BaseModel):
    exercise_id: int
    exercise: str
    sets: int


class RoutineDayOut(BaseModel):
    id: int
    name: str
    items: list[RoutineItemOut]


class RoutineOut(BaseModel):
    id: int
    name: str
    created_by: int
    followers: list[int]
    days: list[RoutineDayOut]


class FollowInput(BaseModel):
    routine_id: int | None
