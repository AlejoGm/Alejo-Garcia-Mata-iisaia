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
    # Pecho
    ("Press inclinado con mancuernas", False), ("Press declinado", False), ("Máquina convergente", False),
    ("Aperturas en polea", False), ("Pec deck", False),
    # Hombros
    ("Press de hombros", False), ("Press Arnold", False), ("Elevaciones laterales en polea", False),
    ("Reverse pec deck", False),
    # Tríceps
    ("Pushdown", False), ("Overhead rope extension", False), ("Single arm extension", False),
    # Espalda
    ("Jalón neutro", False), ("Remo pecho apoyado unilateral", False), ("Pullover en polea", False),
    ("Remo Hammer", False), ("Remo en máquina", False), ("Peso muerto sumo", False),
    # Bíceps
    ("Curl con mancuernas", False), ("Curl en polea", False), ("Curl inclinado", False),
    ("Preacher unilateral", False), ("Hammer preacher", False),
    # Piernas
    ("Hack squat", False), ("Sentadilla en Smith", False), ("Abductores", False), ("Aductores", False),
    # Core
    ("Core", True), ("Plancha con lastre", True),
]

DEFAULT_CHALLENGES = ["Sentadilla", "Press banca", "Peso muerto", "Press militar"]


def find_by_name(session: Session, name: str) -> Exercise | None:
    return session.exec(select(Exercise).where(func.lower(Exercise.name) == name.strip().lower())).first()


def seed_exercises(session: Session) -> None:
    for name, bodyweight in EXERCISES:
        if find_by_name(session, name) is None:
            session.add(Exercise(name=name, bodyweight=bodyweight))
    session.commit()
