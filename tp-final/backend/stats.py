"""Reglas de cálculo de Gym-bro. Funciones puras: no conocen la base ni HTTP (ver docs/spec.md)."""
from dataclasses import dataclass
from datetime import date

# Más allá de 10 repeticiones la fórmula de Epley deja de ser confiable.
MAX_REPS_FOR_1RM = 10

# Coeficientes de OpenPowerlifting: (a, b, c, d, e) de a·p⁴ + b·p³ + c·p² + d·p + e, y el rango de p.
DOTS_COEFFICIENTS = {
    "M": ((-0.0000010930, 0.0007391293, -0.1918759221, 24.0900756, -307.75076), (40.0, 210.0)),
    "F": ((-0.0000010706, 0.0005158568, -0.1126655495, 13.6175032, -57.96288), (40.0, 150.0)),
}


@dataclass(frozen=True)
class SetRecord:
    set_id: int
    session_id: int
    user_id: int
    exercise_id: int
    date: date
    weight_kg: float
    reps: int
    bodyweight_kg: float
    bodyweight_exercise: bool = False
    position: int = 0

    @property
    def load(self) -> float:
        # En dominadas o fondos el peso cargado es lastre: la carga real suma el peso corporal.
        return self.weight_kg + (self.bodyweight_kg if self.bodyweight_exercise else 0)

    @property
    def estimated_1rm(self) -> float | None:
        return estimate_1rm(self.load, self.reps)


def estimate_1rm(load: float, reps: int) -> float | None:
    if reps > MAX_REPS_FOR_1RM:
        return None
    if reps == 1:
        return load
    return load * (1 + reps / 30)


def dots(lifted: float, bodyweight: float, sex: str) -> float:
    (a, b, c, d, e), (low, high) = DOTS_COEFFICIENTS[sex]
    p = min(max(bodyweight, low), high)
    return lifted * 500 / (a * p**4 + b * p**3 + c * p**2 + d * p + e)


def set_dots(record: SetRecord, sex: str) -> float | None:
    value = record.estimated_1rm
    return None if value is None else dots(value, record.bodyweight_kg, sex)


def chronological_key(record: SetRecord) -> tuple:
    return (record.date, record.session_id, record.position, record.set_id)


def absolute_key(record: SetRecord) -> tuple:
    """Mayor carga, después más reps, después la más temprana."""
    return (record.load, record.reps, -record.date.toordinal(), -record.session_id, -record.position)


def best_absolute(records: list[SetRecord]) -> SetRecord | None:
    return max(records, key=absolute_key, default=None)


def best_1rm(records: list[SetRecord]) -> SetRecord | None:
    rated = [r for r in records if r.estimated_1rm is not None]
    return max(rated, key=lambda r: (r.estimated_1rm, -r.date.toordinal()), default=None)


def detect_prs(records: list[SetRecord]) -> dict[int, str]:
    """Para cada serie que es PR, su tipo: "weight" (más carga, o igual carga con más reps) o "1rm"."""
    prs: dict[int, str] = {}
    best_weight: dict[tuple, tuple] = {}
    best_rm: dict[tuple, float] = {}
    for record in sorted(records, key=chronological_key):
        key = (record.user_id, record.exercise_id)
        weight = (record.load, record.reps)
        rm = record.estimated_1rm
        if key in best_weight:
            if weight > best_weight[key]:
                prs[record.set_id] = "weight"
            elif rm is not None and rm > best_rm.get(key, 0):
                prs[record.set_id] = "1rm"
        best_weight[key] = max(best_weight.get(key, weight), weight)
        if rm is not None:
            best_rm[key] = max(best_rm.get(key, 0), rm)
    return prs
