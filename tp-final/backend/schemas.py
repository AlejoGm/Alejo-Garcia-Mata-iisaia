from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator

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
    sets: list[SetOut]


class LastSet(BaseModel):
    display_name: str
    weight_kg: float
    reps: int
    date: date


class LastOut(BaseModel):
    mine: LastSet | None
    others: list[LastSet]


class PeriodOut(BaseModel):
    kind: str
    start: date
    end: date


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


class Person(BaseModel):
    user_id: int
    display_name: str


class DuelInput(BaseModel):
    opponent_id: int
    exercise_id: int
    mode: Literal["absolute", "dots"]
    days: Literal[3, 7, 14] = 7


class DuelOut(BaseModel):
    id: int
    challenger: Person
    opponent: Person
    exercise: str
    exercise_id: int
    mode: str
    days: int
    status: str
    start: date | None
    end: date | None
    challenger_value: float | None
    opponent_value: float | None
    winner_id: int | None


class SuggestionOut(BaseModel):
    user_id: int
    display_name: str
    value: float | None
    level: str
    ratio: float | None


class SuggestionsOut(BaseModel):
    mine: float | None
    rivals: list[SuggestionOut]


class CampaignInput(BaseModel):
    name: Name40
    start: date
    end: date
    tables: Annotated[list[str], Field(min_length=1, max_length=12)]
    routine_id: int | None = None


class StandingRow(BaseModel):
    user_id: int
    display_name: str
    points: int
    firsts: int


class CampaignOut(BaseModel):
    id: int
    name: str
    start: date
    end: date
    tables: list[str]
    table_labels: list[str]
    routine_id: int | None
    status: str
    standings: list[StandingRow]
    winner: Person | None


class MonthPointOut(BaseModel):
    month: date
    best: float | None
    average: float | None


class WeekPointOut(BaseModel):
    week: date
    best: float | None


class BodyweightPointOut(BaseModel):
    week: date
    kg: float


class PersonalStatsOut(BaseModel):
    period: PeriodOut
    exercises: list[ExerciseOut]
    exercise_id: int | None
    months: list[MonthPointOut]
    weeks: list[WeekPointOut]
    bodyweight: list[BodyweightPointOut]
    best_weight_kg: float | None
    best_reps: int | None
    best_1rm: float | None
    sessions: int
