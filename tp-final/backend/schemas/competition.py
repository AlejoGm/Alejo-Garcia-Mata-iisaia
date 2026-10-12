from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from backend.schemas.common import Name40, Person


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
