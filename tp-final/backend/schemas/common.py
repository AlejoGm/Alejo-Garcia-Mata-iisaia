from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, computed_field, field_validator

from backend.catalog import BARBELL

Name30 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]


class ConfigOut(BaseModel):
    auth: Literal["auth0", "local", "dev"]
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

    @computed_field
    @property
    def barbell(self) -> bool:
        return self.name in BARBELL


class Person(BaseModel):
    user_id: int
    display_name: str


class PeriodOut(BaseModel):
    kind: str
    start: date
    end: date


class LoginInput(BaseModel):
    username: Annotated[str, StringConstraints(min_length=1, max_length=30)]
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]

    @field_validator("username", mode="before")
    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip().lower() if isinstance(value, str) else value


class AccountInput(LoginInput):
    """Al registrarse se piden más cosas que al entrar: usuario de 3 a 30 caracteres simples y contraseña de 6."""
    username: Annotated[str, StringConstraints(min_length=3, max_length=30, pattern=r"^[a-z0-9._-]+$")]
    password: Annotated[str, StringConstraints(min_length=6, max_length=128)]


class TokenOut(BaseModel):
    token: str
