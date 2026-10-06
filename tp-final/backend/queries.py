"""Lecturas que arman la entrada del módulo de estadísticas."""
from sqlmodel import Session, func, select

from backend.models import Exercise, GoalChange, Reaction, WorkoutSession, WorkSet
from backend.stats import SetRecord

_COLUMNS = (WorkSet.id, WorkSet.session_id, WorkoutSession.user_id, WorkSet.exercise_id, WorkoutSession.date,
            WorkSet.weight_kg, WorkSet.reps, WorkoutSession.bodyweight_kg, Exercise.bodyweight, WorkSet.position)


def set_records(session: Session, user_ids: list[int], exercise_ids: list[int] | None = None) -> list[SetRecord]:
    if not user_ids:
        return []
    query = (
        select(*_COLUMNS)
        .join(WorkoutSession, WorkSet.session_id == WorkoutSession.id)
        .join(Exercise, WorkSet.exercise_id == Exercise.id)
        .where(WorkoutSession.user_id.in_(user_ids))
    )
    if exercise_ids is not None:
        query = query.where(WorkSet.exercise_id.in_(exercise_ids))
    return [SetRecord(*row) for row in session.exec(query)]


def goal_changes(session: Session, user_ids: list[int]) -> dict[int, list[tuple]]:
    changes: dict[int, list[tuple]] = {user_id: [] for user_id in user_ids}
    for change in session.exec(select(GoalChange).where(GoalChange.user_id.in_(user_ids))):
        changes[change.user_id].append((change.week, change.goal))
    return changes


def excluded_sets(session: Session, group_id: int, member_count: int) -> set[int]:
    """Series que más de la mitad del grupo marcó como dudosas: no cuentan para sus rankings."""
    query = (
        select(Reaction.set_id, func.count()).where(Reaction.group_id == group_id, Reaction.kind == "dudoso")
        .group_by(Reaction.set_id)
    )
    return {set_id for set_id, count in session.exec(query) if count * 2 > member_count}


def group_records(session: Session, group_id: int, user_ids: list[int]) -> list[SetRecord]:
    excluded = excluded_sets(session, group_id, len(user_ids))
    return [r for r in set_records(session, user_ids) if r.set_id not in excluded]
