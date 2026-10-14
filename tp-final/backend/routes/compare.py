from collections import Counter
from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from backend import stats
from backend.auth import SessionDep, UserDep
from backend.models import Exercise
from backend.queries import goal_changes, group_records
from backend.routes.rankings import context
from backend.schemas import CompareOut, ComparePerson, ExerciseOut, PeriodOut

router = APIRouter(prefix="/api")


@router.get("/groups/{code}/compare", response_model=CompareOut)
def compare(code: str, user: UserDep, session: SessionDep, exercise_id: int | None = None,
            metric: Literal["max", "1rm", "dots"] = "dots", period: str = "6m") -> CompareOut:
    ctx = context(session, code, user)
    records = group_records(session, ctx.group.id, ctx.ids)
    today = date.today()
    try:
        low, high = stats.period_range(period, today, first=min((r.date for r in records), default=None))
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    # Del más cargado en el grupo al menos. Con 1RM o DOTS, solo los que tienen 1RM estimable.
    counts = Counter(r.exercise_id for r in records if metric == "max" or r.estimated_1rm is not None)
    found = {e.id: e for e in session.exec(select(Exercise).where(Exercise.id.in_(list(counts))))}
    chosen = exercise_id if exercise_id in counts else (counts.most_common(1)[0][0] if counts else None)
    sexes = {uid: u.sex for uid, u in ctx.users.items()}
    lines = stats.monthly_best_by_user(records, chosen, low, high, sexes, metric) if chosen else {}
    weeks, days = stats.weekly_days_by_user(records, ctx.ids, today)
    changes = goal_changes(session, ctx.ids)
    this_week = stats.monday(today)
    return CompareOut(
        period=PeriodOut(kind=period, start=low, end=high), metric=metric, exercise_id=chosen,
        exercises=[ExerciseOut.model_validate(found[eid], from_attributes=True) for eid, _ in counts.most_common()],
        months=stats.month_list(low, high), weeks=weeks,
        people=[ComparePerson(user_id=uid, display_name=ctx.name(uid), months=lines.get(uid, []), days=days[uid],
                              goal=stats.goal_in_force(changes[uid], this_week)) for uid in ctx.ids],
    )
