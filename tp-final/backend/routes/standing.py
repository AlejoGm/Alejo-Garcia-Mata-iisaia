import math
from datetime import date

from fastapi import APIRouter, HTTPException
from backend import stats
from backend.auth import SessionDep, UserDep
from backend.models import Exercise
from backend.queries import group_records, set_records
from backend.routes.rankings import context, r1
from backend.routes.sessions import STEP_KG
from backend.schemas import NextRivalOut, Person, StandingInput, StandingOut

router = APIRouter(prefix="/api")


def weight_to_pass(rival_dots: float, data: StandingInput, sex: str, step: float) -> float | None:
    """El peso que, a las reps de la serie y con este peso corporal, supera el DOTS del rival."""
    if data.reps > stats.MAX_REPS_FOR_1RM:
        return None
    needed = rival_dots / stats.dots(1, data.bodyweight_kg, sex)
    weight = math.ceil(stats.set_for_1rm(needed, data.reps) / step) * step
    if stats.dots(stats.estimate_1rm(weight, data.reps), data.bodyweight_kg, sex) <= rival_dots:
        weight += step
    return round(weight, 2)


@router.post("/groups/{code}/standing", response_model=StandingOut, status_code=200)
def live_standing(code: str, data: StandingInput, user: UserDep, session: SessionDep) -> StandingOut:
    ctx = context(session, code, user)
    exercise = session.get(Exercise, data.exercise_id)
    if exercise is None:
        raise HTTPException(status_code=422, detail="Ese ejercicio no existe")
    today = date.today()
    attempt = stats.SetRecord(set_id=-1, session_id=-1, user_id=user.id, exercise_id=exercise.id, date=today,
                              weight_kg=data.weight_kg, reps=data.reps, bodyweight_kg=data.bodyweight_kg,
                              bodyweight_exercise=exercise.bodyweight)
    history = set_records(session, [user.id], [exercise.id])
    month = stats.in_range([r for r in group_records(session, ctx.group.id, ctx.ids) if r.exercise_id == exercise.id],
                           stats.month_start(today), today)
    sexes = {uid: u.sex for uid, u in ctx.users.items()}
    table = stats.strength_table(month, sexes, exercise.id, "dots")
    values = {e.user_id: e.value for e in table if e.value is not None}
    value = stats.set_dots(attempt, user.sex)
    result = stats.standing(values, user.id, value)
    rival = None
    if result.next_id is not None:
        weight = None if exercise.bodyweight else weight_to_pass(values[result.next_id], data, user.sex,
                                                                  STEP_KG[user.unit])
        rival = NextRivalOut(user_id=result.next_id, display_name=ctx.name(result.next_id),
                             dots=r1(values[result.next_id]), weight_kg=weight, reps=data.reps)
    return StandingOut(
        pr=stats.detect_prs(history + [attempt]).get(-1), estimated_1rm=r1(attempt.estimated_1rm), dots=r1(value),
        position_before=result.position_before, position=result.position, total=result.total,
        passed=[Person(user_id=uid, display_name=ctx.name(uid)) for uid in result.passed], next=rival,
    )
