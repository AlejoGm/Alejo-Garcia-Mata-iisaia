"""Lecturas que arman la entrada del módulo de estadísticas."""
from sqlmodel import Session, select

from backend.models import Exercise, WorkoutSession, WorkSet
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
