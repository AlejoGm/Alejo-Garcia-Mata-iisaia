from fastapi import APIRouter, HTTPException, Response
from sqlmodel import Session, select, update

from backend.auth import SessionDep, UserDep
from backend.groups import require_member
from backend.models import Exercise, Group, Member, Routine, RoutineDay, RoutineItem, WorkoutSession
from backend.schemas import FollowInput, RoutineDayOut, RoutineInput, RoutineItemOut, RoutineOut

router = APIRouter(prefix="/api")


def routine_out(session: Session, routine: Routine) -> RoutineOut:
    names = {e.id: e.name for e in session.exec(select(Exercise))}
    followers = list(session.exec(select(Member.user_id).where(Member.routine_id == routine.id)))
    days = []
    for day in session.exec(select(RoutineDay).where(RoutineDay.routine_id == routine.id).order_by(RoutineDay.position)):
        items = session.exec(select(RoutineItem).where(RoutineItem.day_id == day.id).order_by(RoutineItem.position))
        days.append(RoutineDayOut(id=day.id, name=day.name, items=[
            RoutineItemOut(exercise_id=i.exercise_id, exercise=names[i.exercise_id], sets=i.sets) for i in items]))
    return RoutineOut(id=routine.id, name=routine.name, created_by=routine.created_by, followers=followers, days=days)


def find_routine(session: Session, group: Group, routine_id: int) -> Routine:
    routine = session.get(Routine, routine_id)
    if routine is None or routine.group_id != group.id:
        raise HTTPException(status_code=404, detail="Esa rutina no existe en este grupo")
    return routine


def write_days(session: Session, routine: Routine, data: RoutineInput) -> None:
    ids = {item.exercise_id for day in data.days for item in day.items}
    if len(session.exec(select(Exercise.id).where(Exercise.id.in_(ids))).all()) != len(ids):
        raise HTTPException(status_code=422, detail="Hay un ejercicio que no existe")
    for position, day_data in enumerate(data.days):
        day = RoutineDay(routine_id=routine.id, name=day_data.name, position=position)
        session.add(day)
        session.flush()
        for item_position, item in enumerate(day_data.items):
            session.add(RoutineItem(day_id=day.id, exercise_id=item.exercise_id, sets=item.sets, position=item_position))


def clear_days(session: Session, routine: Routine) -> None:
    day_ids = list(session.exec(select(RoutineDay.id).where(RoutineDay.routine_id == routine.id)))
    # Las sesiones ya cargadas conservan sus series; solo pierden el vínculo con el día borrado.
    session.exec(update(WorkoutSession).where(WorkoutSession.routine_day_id.in_(day_ids)).values(routine_day_id=None))
    for item in session.exec(select(RoutineItem).where(RoutineItem.day_id.in_(day_ids))):
        session.delete(item)
    for day in session.exec(select(RoutineDay).where(RoutineDay.id.in_(day_ids))):
        session.delete(day)
    session.flush()


@router.get("/groups/{code}/routines", response_model=list[RoutineOut])
def list_routines(code: str, user: UserDep, session: SessionDep) -> list[RoutineOut]:
    group, _ = require_member(session, code, user)
    routines = session.exec(select(Routine).where(Routine.group_id == group.id).order_by(Routine.name))
    return [routine_out(session, r) for r in routines]


@router.post("/groups/{code}/routines", response_model=RoutineOut, status_code=201)
def create_routine(code: str, data: RoutineInput, user: UserDep, session: SessionDep) -> RoutineOut:
    group, _ = require_member(session, code, user)
    routine = Routine(group_id=group.id, name=data.name, created_by=user.id)
    session.add(routine)
    session.flush()
    write_days(session, routine, data)
    session.commit()
    return routine_out(session, routine)


@router.put("/groups/{code}/routines/{routine_id}", response_model=RoutineOut)
def replace_routine(code: str, routine_id: int, data: RoutineInput, user: UserDep, session: SessionDep) -> RoutineOut:
    group, _ = require_member(session, code, user)
    routine = find_routine(session, group, routine_id)
    clear_days(session, routine)
    routine.name = data.name
    write_days(session, routine, data)
    session.commit()
    return routine_out(session, routine)


@router.delete("/groups/{code}/routines/{routine_id}", status_code=204)
def delete_routine(code: str, routine_id: int, user: UserDep, session: SessionDep) -> Response:
    group, _ = require_member(session, code, user)
    routine = find_routine(session, group, routine_id)
    clear_days(session, routine)
    session.exec(update(Member).where(Member.routine_id == routine.id).values(routine_id=None))
    session.delete(routine)
    session.commit()
    return Response(status_code=204)


@router.put("/groups/{code}/members/me/routine", status_code=200)
def follow_routine(code: str, data: FollowInput, user: UserDep, session: SessionDep) -> dict:
    group, member = require_member(session, code, user)
    if data.routine_id is not None:
        routine = session.get(Routine, data.routine_id)
        if routine is None or routine.group_id != group.id:
            raise HTTPException(status_code=422, detail="Esa rutina no es de este grupo")
    member.routine_id = data.routine_id
    session.commit()
    return {"routine_id": data.routine_id}
