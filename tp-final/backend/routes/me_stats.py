from collections import Counter
from datetime import date

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select

from backend import stats
from backend.auth import SessionDep, UserDep
from backend.catalog import MUSCLES, lift_ids
from backend.models import Exercise
from backend.queries import goal_changes, set_records
from backend.schemas import (
    AchievementOut, BodyweightPointOut, DayCountOut, ExerciseOut, MuscleSetsOut, MonthPointOut, PeriodOut, PersonalStatsOut, WeekPointOut,
)

router = APIRouter(prefix="/api")


def muscle_ids(session: Session) -> dict[int, str]:
    return {e.id: MUSCLES[e.name] for e in session.exec(select(Exercise)) if e.name in MUSCLES}


def achievements_of(session: Session, user_ids: list[int], today: date) -> dict[int, list[stats.Achievement]]:
    """Medallas de cada usuario, con todo su historial: son personales, no dependen del grupo."""
    records = stats.by_user(set_records(session, user_ids))
    changes = goal_changes(session, user_ids)
    lifts = lift_ids(session)
    return {uid: stats.achievements(records.get(uid, []), changes[uid], lifts, today) for uid in user_ids}


def achievements_out(earned: list[stats.Achievement]) -> list[AchievementOut]:
    days = {a.key: a.day for a in earned}
    return [AchievementOut(key=key, title=title, description=text, day=days.get(key))
            for key, (title, text) in stats.ACHIEVEMENTS.items()]


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
        achievements=achievements_out(achievements_of(session, [user.id], date.today())[user.id]),
        calendar=[DayCountOut(day=d.day, sets=d.sets) for d in stats.training_calendar(records, date.today())],
        muscles=[MuscleSetsOut(**m.__dict__) for m in stats.muscle_sets(records, muscle_ids(session), date.today())],
    )
