from datetime import date

from pydantic import BaseModel

from backend.schemas.common import ExerciseOut, PeriodOut


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


class AchievementOut(BaseModel):
    key: str
    title: str
    description: str
    day: date | None


class MedalOut(BaseModel):
    user_id: int
    display_name: str
    key: str
    title: str
    day: date


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
    sessions: int  # sesiones del período con este ejercicio
    achievements: list[AchievementOut]


class WeekActivityOut(BaseModel):
    week: date
    sessions: int
    volume: float


class DayActivityOut(BaseModel):
    day: date
    members: int
    mine: bool


class LeaderOut(BaseModel):
    exercise: str
    user_id: int
    display_name: str
    value: float


class StreakOut(BaseModel):
    user_id: int
    display_name: str
    weeks: int


class DashboardOut(BaseModel):
    sessions: int
    sessions_prev: int
    volume: float
    volume_prev: float
    prs_month: int
    prs_prev_month: int
    best_streak: StreakOut | None
    series: list[WeekActivityOut]
    days: list[DayActivityOut]
    goal_pct: float | None
    leaders: list[LeaderOut]
    medals: list[MedalOut]
