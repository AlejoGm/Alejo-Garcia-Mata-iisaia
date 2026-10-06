from collections import Counter
from datetime import date

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from backend import stats
from backend.auth import SessionDep, UserDep
from backend.models import Exercise
from backend.queries import set_records
from backend.schemas import (
    BodyweightPointOut, ExerciseOut, MonthPointOut, PeriodOut, PersonalStatsOut, WeekPointOut,
)

router = APIRouter(prefix="/api")


@router.get("/me/stats", response_model=PersonalStatsOut)
def personal_stats(user: UserDep, session: SessionDep, exercise_id: int | None = None, period: str = "6m",
                   month: str | None = None, start: str | None = Query(None, alias="from"),
                   end: str | None = Query(None, alias="to")) -> PersonalStatsOut:
    records = set_records(session, [user.id])
    try:
        low, high = stats.period_range(period, date.today(), month=month, start=start, end=end,
                                       first=min((r.date for r in records), default=None))
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    counts = Counter(r.exercise_id for r in records)
    exercises = {e.id: e for e in session.exec(select(Exercise).where(Exercise.id.in_(list(counts))))}
    chosen = exercise_id if exercise_id is not None else (counts.most_common(1)[0][0] if counts else None)
    mine = [r for r in records if r.exercise_id == chosen]
    best_abs = stats.best_absolute(mine)
    best_rm = stats.best_1rm(mine)
    return PersonalStatsOut(
        period=PeriodOut(kind=period, start=low, end=high),
        exercises=[ExerciseOut.model_validate(exercises[eid], from_attributes=True) for eid, _ in counts.most_common()],
        exercise_id=chosen,
        months=[MonthPointOut(**p.__dict__) for p in stats.monthly_series(records, chosen, low, high)] if chosen else [],
        weeks=[WeekPointOut(**p.__dict__) for p in stats.weekly_series(records, chosen, low, high)] if chosen else [],
        bodyweight=[BodyweightPointOut(**p.__dict__) for p in stats.bodyweight_series(records, low, high)],
        best_weight_kg=best_abs.weight_kg if best_abs else None,
        best_reps=best_abs.reps if best_abs else None,
        best_1rm=round(best_rm.estimated_1rm, 1) if best_rm else None,
        sessions=len({r.session_id for r in stats.in_range(mine, low, high)}),
    )
