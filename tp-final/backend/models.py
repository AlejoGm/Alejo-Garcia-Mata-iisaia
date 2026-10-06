from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel, UniqueConstraint


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sub: str = Field(unique=True, index=True)
    display_name: str
    sex: str  # "M" o "F", para DOTS
    unit: str = "kg"
    created_at: datetime = Field(default_factory=now_utc)


class GoalChange(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "week"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    goal: int
    week: date  # lunes desde el que rige


class Group(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    name: str
    created_at: datetime = Field(default_factory=now_utc)


class Member(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("group_id", "user_id"),)

    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="group.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    is_admin: bool = False
    joined_at: datetime = Field(default_factory=now_utc)
    routine_id: int | None = Field(default=None, foreign_key="routine.id")


class Exercise(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    bodyweight: bool = False  # el peso cargado es lastre sobre el peso corporal


class Challenge(SQLModel, table=True):
    group_id: int = Field(foreign_key="group.id", primary_key=True)
    exercise_id: int = Field(foreign_key="exercise.id", primary_key=True)


class Routine(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="group.id", index=True)
    name: str
    created_by: int = Field(foreign_key="user.id")


class WorkoutSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    date: date
    bodyweight_kg: float
    routine_day_id: int | None = Field(default=None, foreign_key="routineday.id")
    created_at: datetime = Field(default_factory=now_utc)


class WorkSet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="workoutsession.id", index=True)
    exercise_id: int = Field(foreign_key="exercise.id", index=True)
    weight_kg: float
    reps: int
    position: int = 0


class RoutineDay(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routine.id", index=True)
    name: str
    position: int = 0


class RoutineItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    day_id: int = Field(foreign_key="routineday.id", index=True)
    exercise_id: int = Field(foreign_key="exercise.id")
    sets: int
    position: int = 0


class Reaction(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("group_id", "set_id", "user_id"),)

    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="group.id", index=True)
    set_id: int = Field(foreign_key="workset.id", index=True)
    user_id: int = Field(foreign_key="user.id")
    kind: str  # "fuerza", "fuego" o "dudoso"


class Duel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="group.id", index=True)
    challenger_id: int = Field(foreign_key="user.id")
    opponent_id: int = Field(foreign_key="user.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    mode: str  # "absolute" o "dots"
    days: int
    status: str = "pending"  # "pending", "active" o "rejected"; "finished" se deriva de la fecha
    created_at: datetime = Field(default_factory=now_utc)
    start: date | None = None


class Campaign(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="group.id", index=True)
    name: str
    start: date
    end: date
    tables: str  # JSON: lista de claves "dots:<id>", "absolute:<id>", "progress", "consistency"
    routine_id: int | None = Field(default=None, foreign_key="routine.id")
    winner_id: int | None = Field(default=None, foreign_key="user.id")
    frozen_at: datetime | None = None
