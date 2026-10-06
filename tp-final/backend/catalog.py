from sqlmodel import Session, func, select

from backend.models import Exercise

# (nombre, de peso corporal)
EXERCISES = [
    ("Sentadilla", False), ("Press banca", False), ("Peso muerto", False), ("Press militar", False),
    ("Press inclinado", False), ("Press con mancuernas", False), ("Aperturas", False), ("Fondos", True),
    ("Flexiones", True), ("Dominadas", True), ("Jalón al pecho", False), ("Remo con barra", False),
    ("Remo con mancuerna", False), ("Remo en polea", False), ("Face pull", False), ("Vuelos laterales", False),
    ("Curl de bíceps", False), ("Curl martillo", False), ("Extensión de tríceps", False), ("Press francés", False),
    ("Sentadilla frontal", False), ("Sentadilla búlgara", False), ("Prensa", False), ("Zancadas", False),
    ("Hip thrust", False), ("Peso muerto rumano", False), ("Extensión de cuádriceps", False),
    ("Curl femoral", False), ("Elevación de talones", False), ("Abdominales en polea", False),
]

DEFAULT_CHALLENGES = ["Sentadilla", "Press banca", "Peso muerto", "Press militar"]


def find_by_name(session: Session, name: str) -> Exercise | None:
    return session.exec(select(Exercise).where(func.lower(Exercise.name) == name.strip().lower())).first()


def seed_exercises(session: Session) -> None:
    for name, bodyweight in EXERCISES:
        if find_by_name(session, name) is None:
            session.add(Exercise(name=name, bodyweight=bodyweight))
    session.commit()
