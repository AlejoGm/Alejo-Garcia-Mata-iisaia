from typing import Annotated

from pydantic import BaseModel, Field

from backend.schemas.common import Name40, ExerciseOut


class GroupInput(BaseModel):
    name: Name40


class GroupSummary(BaseModel):
    code: str
    name: str
    is_admin: bool
    members: int


class MemberOut(BaseModel):
    user_id: int
    display_name: str
    is_admin: bool
    routine_id: int | None


class GroupDetail(BaseModel):
    code: str
    name: str
    is_admin: bool
    me: int
    members: list[MemberOut]
    challenges: list[ExerciseOut]


class ChallengesInput(BaseModel):
    exercise_ids: Annotated[list[int], Field(max_length=4)]
