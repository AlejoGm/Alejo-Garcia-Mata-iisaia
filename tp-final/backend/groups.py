"""Búsquedas y chequeos de pertenencia que comparten todas las rutas de grupo."""
import secrets

from fastapi import HTTPException
from sqlmodel import Session, select

from backend.models import Challenge, Exercise, Group, Member, User

# Sin 0/O ni 1/I: el código se dicta por chat o en voz alta.
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def new_code(session: Session) -> str:
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(6))
        if session.exec(select(Group).where(Group.code == code)).first() is None:
            return code


def find_group(session: Session, code: str) -> Group:
    group = session.exec(select(Group).where(Group.code == code.upper())).first()
    if group is None:
        raise HTTPException(status_code=404, detail=f"El grupo '{code}' no existe")
    return group


def membership(session: Session, group: Group, user: User) -> Member | None:
    return session.exec(select(Member).where(Member.group_id == group.id, Member.user_id == user.id)).first()


def require_member(session: Session, code: str, user: User) -> tuple[Group, Member]:
    group = find_group(session, code)
    member = membership(session, group, user)
    if member is None:
        raise HTTPException(status_code=403, detail="No sos miembro de este grupo")
    return group, member


def require_admin(session: Session, code: str, user: User) -> tuple[Group, Member]:
    group, member = require_member(session, code, user)
    if not member.is_admin:
        raise HTTPException(status_code=403, detail="Solo el admin del grupo puede hacer esto")
    return group, member


def members_with_users(session: Session, group: Group) -> list[tuple[Member, User]]:
    query = (
        select(Member, User).join(User, Member.user_id == User.id)
        .where(Member.group_id == group.id).order_by(Member.joined_at, Member.id)
    )
    return list(session.exec(query))


def challenge_exercises(session: Session, group: Group) -> list[Exercise]:
    query = (
        select(Exercise).join(Challenge, Challenge.exercise_id == Exercise.id)
        .where(Challenge.group_id == group.id).order_by(Exercise.id)
    )
    return list(session.exec(query))
