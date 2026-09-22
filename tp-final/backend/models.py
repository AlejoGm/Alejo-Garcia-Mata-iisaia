from datetime import date

from sqlmodel import Field, SQLModel, UniqueConstraint


class Group(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    name: str


class Member(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("group_id", "nickname"),)

    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="group.id", index=True)
    nickname: str
    bodyweight_kg: float


class Exercise(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("group_id", "name"),)

    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="group.id", index=True)
    name: str
    is_challenge: bool = False


class WorkoutSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="member.id", index=True)
    date: date


class WorkSet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="workoutsession.id", index=True)
    exercise_id: int = Field(foreign_key="exercise.id")
    weight_kg: float
    reps: int
