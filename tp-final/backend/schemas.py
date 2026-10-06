from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

Name30 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]


class ConfigOut(BaseModel):
    auth: Literal["auth0", "dev"]
    domain: str
    client_id: str
    audience: str


class ProfileInput(BaseModel):
    display_name: Name30
    sex: Literal["M", "F"]
    weekly_goal: Annotated[int, Field(ge=1, le=7)]
    unit: Literal["kg", "lb"] = "kg"


class ProfileOut(BaseModel):
    id: int
    display_name: str
    sex: str
    unit: str
    weekly_goal: int | None
    next_week_goal: int | None
    last_bodyweight_kg: float | None

Name40 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]


class ExerciseInput(BaseModel):
    name: Name40
    bodyweight: bool = False


class ExerciseOut(BaseModel):
    id: int
    name: str
    bodyweight: bool


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
