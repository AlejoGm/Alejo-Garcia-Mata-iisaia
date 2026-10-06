from fastapi import APIRouter, HTTPException, Query, Response
from sqlmodel import Session, delete, select

from backend import stats
from backend.auth import SessionDep, UserDep
from backend.groups import members_with_users, require_member
from backend.models import Exercise, Reaction, RoutineDay, User, WorkoutSession, WorkSet
from backend.queries import set_records
from backend.schemas import LastOut, LastSet, SessionInput, SessionOut, SetOut

router = APIRouter(prefix="/api")


def round1(value: float | None) -> float | None:
    return None if value is None else round(value, 1)


def sessions_out(session: Session, user: User, workouts: list[WorkoutSession]) -> list[SessionOut]:
    if not workouts:
        return []
    records = set_records(session, [user.id])
    prs = stats.detect_prs(records)
    by_set = {r.set_id: r for r in records}
    names = {e.id: e.name for e in session.exec(select(Exercise))}
    day_ids = {w.routine_day_id for w in workouts if w.routine_day_id}
    day_names = {d.id: d.name for d in session.exec(select(RoutineDay).where(RoutineDay.id.in_(day_ids)))}
    sets_by_session: dict[int, list[WorkSet]] = {}
    ids = [w.id for w in workouts]
    for work_set in session.exec(select(WorkSet).where(WorkSet.session_id.in_(ids)).order_by(WorkSet.position)):
        sets_by_session.setdefault(work_set.session_id, []).append(work_set)

    def set_out(s: WorkSet) -> SetOut:
        r = by_set[s.id]
        return SetOut(id=s.id, exercise_id=s.exercise_id, exercise=names[s.exercise_id], weight_kg=s.weight_kg,
                      reps=s.reps, load=round1(r.load), estimated_1rm=round1(r.estimated_1rm),
                      dots=round1(stats.set_dots(r, user.sex)), pr=prs.get(s.id))

    return [SessionOut(id=w.id, date=w.date, bodyweight_kg=w.bodyweight_kg, routine_day_id=w.routine_day_id,
                       routine_day_name=day_names.get(w.routine_day_id),
                       sets=[set_out(s) for s in sets_by_session.get(w.id, [])]) for w in workouts]


def validate_sets(session: Session, data: SessionInput) -> None:
    ids = {s.exercise_id for s in data.sets}
    exercises = {e.id: e for e in session.exec(select(Exercise).where(Exercise.id.in_(ids)))}
    if len(exercises) != len(ids):
        raise HTTPException(status_code=422, detail="Hay un ejercicio que no existe")
    for s in data.sets:
        if s.weight_kg <= 0 and not exercises[s.exercise_id].bodyweight:
            raise HTTPException(status_code=422, detail=f"Falta el peso en {exercises[s.exercise_id].name}")
    if data.routine_day_id is not None and session.get(RoutineDay, data.routine_day_id) is None:
        raise HTTPException(status_code=422, detail="Ese día de rutina no existe")


@router.post("/me/sessions", response_model=SessionOut, status_code=201)
def create_session(data: SessionInput, user: UserDep, session: SessionDep) -> SessionOut:
    validate_sets(session, data)
    workout = WorkoutSession(user_id=user.id, date=data.date, bodyweight_kg=data.bodyweight_kg,
                             routine_day_id=data.routine_day_id)
    session.add(workout)
    session.flush()
    for position, s in enumerate(data.sets):
        session.add(WorkSet(session_id=workout.id, exercise_id=s.exercise_id, weight_kg=s.weight_kg, reps=s.reps,
                            position=position))
    session.commit()
    session.refresh(workout)
    return sessions_out(session, user, [workout])[0]


@router.get("/me/sessions", response_model=list[SessionOut])
def list_sessions(user: UserDep, session: SessionDep, limit: int = Query(20, ge=1, le=100)) -> list[SessionOut]:
    query = (select(WorkoutSession).where(WorkoutSession.user_id == user.id)
             .order_by(WorkoutSession.date.desc(), WorkoutSession.id.desc()).limit(limit))
    return sessions_out(session, user, list(session.exec(query)))


@router.delete("/me/sessions/{session_id}", status_code=204)
def delete_session(session_id: int, user: UserDep, session: SessionDep) -> Response:
    workout = session.get(WorkoutSession, session_id)
    if workout is None or workout.user_id != user.id:
        raise HTTPException(status_code=404, detail="Esa sesión no existe")
    set_ids = select(WorkSet.id).where(WorkSet.session_id == workout.id)
    session.exec(delete(Reaction).where(Reaction.set_id.in_(set_ids)))
    session.exec(delete(WorkSet).where(WorkSet.session_id == workout.id))
    session.delete(workout)
    session.commit()
    return Response(status_code=204)


def last_set_of(session: Session, user_id: int, exercise_id: int) -> tuple[WorkSet, WorkoutSession] | None:
    """La serie más pesada de la última sesión con ese ejercicio."""
    query = (
        select(WorkSet, WorkoutSession).join(WorkoutSession, WorkSet.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == user_id, WorkSet.exercise_id == exercise_id)
        .order_by(WorkoutSession.date.desc(), WorkoutSession.id.desc(),
                  WorkSet.weight_kg.desc(), WorkSet.reps.desc())
    )
    return session.exec(query).first()


@router.get("/groups/{code}/last", response_model=LastOut)
def last_sets(code: str, exercise_id: int, user: UserDep, session: SessionDep) -> LastOut:
    group, _ = require_member(session, code, user)
    found = []
    for _member, member_user in members_with_users(session, group):
        last = last_set_of(session, member_user.id, exercise_id)
        if last:
            work_set, workout = last
            found.append((member_user, LastSet(display_name=member_user.display_name, weight_kg=work_set.weight_kg,
                                               reps=work_set.reps, date=workout.date)))
    mine = next((entry for u, entry in found if u.id == user.id), None)
    others = sorted((entry for u, entry in found if u.id != user.id), key=lambda e: e.date, reverse=True)[:2]
    return LastOut(mine=mine, others=others)
