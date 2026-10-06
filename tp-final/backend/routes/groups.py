from fastapi import APIRouter, HTTPException, Response
from sqlmodel import Session, func, select

from backend.auth import SessionDep, UserDep
from backend.catalog import DEFAULT_CHALLENGES, find_by_name
from backend.groups import (
    challenge_exercises, find_group, members_with_users, membership, new_code, require_admin, require_member,
)
from backend.models import Challenge, Exercise, Group, Member, User
from backend.schemas import (
    ChallengesInput, ExerciseOut, GroupDetail, GroupInput, GroupSummary, MemberOut,
)

router = APIRouter(prefix="/api")


def summary(session: Session, group: Group, member: Member) -> GroupSummary:
    count = session.exec(select(func.count()).select_from(Member).where(Member.group_id == group.id)).one()
    return GroupSummary(code=group.code, name=group.name, is_admin=member.is_admin, members=count)


@router.get("/me/groups", response_model=list[GroupSummary])
def my_groups(user: UserDep, session: SessionDep) -> list[GroupSummary]:
    query = select(Group, Member).join(Member, Member.group_id == Group.id).where(Member.user_id == user.id)
    return [summary(session, group, member) for group, member in session.exec(query.order_by(Group.name))]


@router.post("/groups", response_model=GroupSummary, status_code=201)
def create_group(data: GroupInput, user: UserDep, session: SessionDep) -> GroupSummary:
    group = Group(code=new_code(session), name=data.name)
    session.add(group)
    session.flush()
    member = Member(group_id=group.id, user_id=user.id, is_admin=True)
    session.add(member)
    for name in DEFAULT_CHALLENGES:
        exercise = find_by_name(session, name)
        if exercise:
            session.add(Challenge(group_id=group.id, exercise_id=exercise.id))
    session.commit()
    return summary(session, group, member)


@router.get("/groups/{code}", response_model=GroupDetail)
def get_group(code: str, user: UserDep, session: SessionDep) -> GroupDetail:
    group, member = require_member(session, code, user)
    return GroupDetail(
        code=group.code,
        name=group.name,
        is_admin=member.is_admin,
        me=user.id,
        members=[
            MemberOut(user_id=u.id, display_name=u.display_name, is_admin=m.is_admin, routine_id=m.routine_id)
            for m, u in members_with_users(session, group)
        ],
        challenges=[ExerciseOut.model_validate(e, from_attributes=True) for e in challenge_exercises(session, group)],
    )


@router.post("/groups/{code}/join", response_model=GroupSummary, status_code=201)
def join_group(code: str, user: UserDep, session: SessionDep) -> GroupSummary:
    group = find_group(session, code)
    if membership(session, group, user):
        raise HTTPException(status_code=409, detail="Ya sos miembro de este grupo")
    member = Member(group_id=group.id, user_id=user.id)
    session.add(member)
    session.commit()
    return summary(session, group, member)


def remove_member(session: Session, group: Group, member: Member) -> None:
    session.delete(member)
    session.flush()
    if member.is_admin:
        # El rol pasa al miembro más antiguo que queda.
        heir = session.exec(
            select(Member).where(Member.group_id == group.id).order_by(Member.joined_at, Member.id)
        ).first()
        if heir:
            heir.is_admin = True
    session.commit()


@router.delete("/groups/{code}/members/me", status_code=204)
def leave_group(code: str, user: UserDep, session: SessionDep) -> Response:
    group, member = require_member(session, code, user)
    remove_member(session, group, member)
    return Response(status_code=204)


@router.delete("/groups/{code}/members/{user_id}", status_code=204)
def kick_member(code: str, user_id: int, user: UserDep, session: SessionDep) -> Response:
    group, _ = require_admin(session, code, user)
    if user_id == user.id:
        raise HTTPException(status_code=422, detail="Para irte usá 'Salir del grupo'")
    target = session.get(User, user_id)
    member = membership(session, group, target) if target else None
    if member is None:
        raise HTTPException(status_code=404, detail="Esa persona no es miembro del grupo")
    remove_member(session, group, member)
    return Response(status_code=204)


@router.put("/groups/{code}/challenges", response_model=list[ExerciseOut])
def set_challenges(code: str, data: ChallengesInput, user: UserDep, session: SessionDep) -> list[Exercise]:
    group, _ = require_admin(session, code, user)
    ids = list(dict.fromkeys(data.exercise_ids))
    if len(session.exec(select(Exercise).where(Exercise.id.in_(ids))).all()) != len(ids):
        raise HTTPException(status_code=422, detail="Hay un ejercicio que no existe")
    for old in session.exec(select(Challenge).where(Challenge.group_id == group.id)):
        session.delete(old)
    session.flush()
    for exercise_id in ids:
        session.add(Challenge(group_id=group.id, exercise_id=exercise_id))
    session.commit()
    return challenge_exercises(session, group)
