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
