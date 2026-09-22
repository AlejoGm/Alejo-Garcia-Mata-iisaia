import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from backend import stats
from backend.db import get_session
from backend.models import Exercise, Group, Member, WorkoutSession, WorkSet
from backend.schemas import (
    ExerciseOut, GroupDetail, GroupInput, GroupOut, MemberInput, MemberOut, RankingsOut,
    SessionInput, SessionOut, SetOut, StrengthEntryOut, StrengthRankingOut,
)

router = APIRouter(prefix="/api")

SessionDep = Annotated[Session, Depends(get_session)]

# Sin 0/O ni 1/I: el código se dicta por chat o en voz alta.
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 6
DEFAULT_CHALLENGES = ["Sentadilla", "Press banca", "Peso muerto", "Press militar"]


def new_code(session: Session) -> str:
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        if session.exec(select(Group).where(Group.code == code)).first() is None:
            return code


def find_group(session: Session, code: str) -> Group:
    group = session.exec(select(Group).where(Group.code == code.upper())).first()
    if group is None:
        raise HTTPException(status_code=404, detail=f"El grupo '{code}' no existe")
    return group


def find_member(session: Session, group: Group, nickname: str) -> Member | None:
    query = select(Member).where(Member.group_id == group.id, func.lower(Member.nickname) == nickname.lower())
    return session.exec(query).first()


def group_exercises(session: Session, group: Group) -> list[Exercise]:
    return list(session.exec(select(Exercise).where(Exercise.group_id == group.id).order_by(Exercise.id)))


def group_members(session: Session, group: Group) -> list[Member]:
    return list(session.exec(select(Member).where(Member.group_id == group.id).order_by(Member.id)))


@router.post("/groups", response_model=GroupOut, status_code=201)
def create_group(data: GroupInput, session: SessionDep) -> Group:
    group = Group(code=new_code(session), name=data.name)
    session.add(group)
    session.flush()
    for name in DEFAULT_CHALLENGES:
        session.add(Exercise(group_id=group.id, name=name, is_challenge=True))
    session.commit()
    session.refresh(group)
    return group


@router.get("/groups/{code}", response_model=GroupDetail)
def get_group(code: str, session: SessionDep) -> GroupDetail:
    group = find_group(session, code)
    return GroupDetail(
        code=group.code,
        name=group.name,
        members=[MemberOut.model_validate(m, from_attributes=True) for m in group_members(session, group)],
        exercises=[ExerciseOut.model_validate(e, from_attributes=True) for e in group_exercises(session, group)],
    )


@router.post("/groups/{code}/members", response_model=MemberOut, status_code=201)
def join_group(code: str, data: MemberInput, session: SessionDep) -> Member:
    group = find_group(session, code)
    if find_member(session, group, data.nickname) is not None:
        raise HTTPException(status_code=409, detail=f"El nickname '{data.nickname}' ya está en uso en este grupo")
    member = Member(group_id=group.id, nickname=data.nickname, bodyweight_kg=data.bodyweight_kg)
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


@router.post("/groups/{code}/members/{nickname}/sessions", response_model=SessionOut, status_code=201)
def create_session(code: str, nickname: str, data: SessionInput, session: SessionDep) -> SessionOut:
    group = find_group(session, code)
    member = find_member(session, group, nickname)
    if member is None:
        raise HTTPException(status_code=404, detail=f"'{nickname}' no es miembro del grupo")
    exercises = {e.id: e for e in group_exercises(session, group)}
    # El ejercicio viaja en el body: si no es del grupo, lo inválido es el contenido, no el path.
    if any(s.exercise_id not in exercises for s in data.sets):
        raise HTTPException(status_code=422, detail="Hay un ejercicio que no pertenece a este grupo")

    workout = WorkoutSession(member_id=member.id, date=data.date)
    session.add(workout)
    session.flush()
    for s in data.sets:
        session.add(WorkSet(session_id=workout.id, exercise_id=s.exercise_id, weight_kg=s.weight_kg, reps=s.reps))
    session.commit()

    sets = [
        SetOut(
            exercise_id=s.exercise_id,
            exercise=exercises[s.exercise_id].name,
            weight_kg=s.weight_kg,
            reps=s.reps,
            estimated_1rm=round_or_none(stats.estimate_1rm(s.weight_kg, s.reps), 1),
        )
        for s in data.sets
    ]
    return SessionOut(id=workout.id, date=workout.date, sets=sets)


@router.get("/groups/{code}/rankings", response_model=RankingsOut)
def get_rankings(code: str, session: SessionDep) -> RankingsOut:
    group = find_group(session, code)
    members = group_members(session, group)
    exercises = group_exercises(session, group)
    challenges = [e.name for e in exercises if e.is_challenge]
    ranking = stats.strength_ranking(
        load_set_records(session, group),
        {m.nickname: m.bodyweight_kg for m in members},
        challenges,
    )
    return RankingsOut(strength=[
        StrengthRankingOut(exercise=name, entries=[
            StrengthEntryOut(nickname=e.member, best_1rm=round_or_none(e.best_1rm, 1), ratio=round_or_none(e.ratio, 2))
            for e in ranking[name]
        ])
        for name in challenges
    ])


def load_set_records(session: Session, group: Group) -> list[stats.SetRecord]:
    query = (
        select(Member.nickname, Exercise.name, WorkoutSession.date, WorkSet.weight_kg, WorkSet.reps)
        .join(WorkoutSession, WorkSet.session_id == WorkoutSession.id)
        .join(Member, WorkoutSession.member_id == Member.id)
        .join(Exercise, WorkSet.exercise_id == Exercise.id)
        .where(Member.group_id == group.id)
    )
    return [stats.SetRecord(*row) for row in session.exec(query)]


def round_or_none(value: float | None, digits: int) -> float | None:
    return None if value is None else round(value, digits)
