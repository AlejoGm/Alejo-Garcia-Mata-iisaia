"""Reglas de cálculo de Gym-bro. Funciones puras: no conocen la base ni HTTP (ver docs/spec.md)."""
import calendar
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

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



# Períodos: rangos de meses de calendario.

def month_start(day: date) -> date:
    return day.replace(day=1)


def month_end(day: date) -> date:
    return day.replace(day=calendar.monthrange(day.year, day.month)[1])


def shift_months(day: date, months: int) -> date:
    index = day.year * 12 + day.month - 1 + months
    return date(index // 12, index % 12 + 1, 1)


def parse_month(text: str) -> date:
    try:
        year, month = (int(part) for part in text.split("-"))
        return date(year, month, 1)
    except (ValueError, AttributeError) as err:
        raise ValueError(f"Mes inválido: {text!r}; usá YYYY-MM") from err


def period_range(kind: str, today: date, month: str | None = None, start: str | None = None,
                 end: str | None = None, first: date | None = None) -> tuple[date, date]:
    current = month_start(today)
    if kind == "month":
        chosen = parse_month(month) if month else current
        return chosen, month_end(chosen)
    if kind in ("6m", "12m"):
        return shift_months(current, -5 if kind == "6m" else -11), month_end(current)
    if kind == "all":
        return month_start(first) if first else current, month_end(current)
    if kind == "custom":
        if not start or not end:
            raise ValueError("Un período a mano necesita desde y hasta")
        low, high = parse_month(start), parse_month(end)
        if low > high:
            raise ValueError("El período empieza después de terminar")
        return low, month_end(high)
    raise ValueError(f"Período desconocido: {kind!r}")


def in_range(records: list[SetRecord], start: date, end: date) -> list[SetRecord]:
    return [r for r in records if start <= r.date <= end]


def by_user(records: list[SetRecord]) -> dict[int, list[SetRecord]]:
    grouped: dict[int, list[SetRecord]] = defaultdict(list)
    for record in records:
        grouped[record.user_id].append(record)
    return grouped


# Fuerza

@dataclass(frozen=True)
class StrengthEntry:
    user_id: int
    value: float | None
    weight_kg: float | None = None
    reps: int | None = None
    day: date | None = None


def strength_table(records: list[SetRecord], sexes: dict[int, str], exercise_id: int,
                   mode: str) -> list[StrengthEntry]:
    """Mejor marca de cada miembro en un ejercicio: DOTS del 1RM estimado, o absoluto. Sin datos al final."""
    grouped = by_user([r for r in records if r.exercise_id == exercise_id])
    rated: list[tuple[tuple, StrengthEntry]] = []
    missing = []
    for user_id, sex in sexes.items():
        mine = grouped.get(user_id, [])
        if mode == "dots":
            scored = [(set_dots(r, sex), r) for r in mine if r.estimated_1rm is not None]
            best = max(scored, key=lambda pair: (pair[0], -pair[1].date.toordinal()), default=None)
            if best:
                value, r = best
                rated.append(((value,), StrengthEntry(user_id, value, r.weight_kg, r.reps, r.date)))
                continue
        else:
            r = best_absolute(mine)
            if r:
                rated.append((absolute_key(r), StrengthEntry(user_id, r.load, r.weight_kg, r.reps, r.date)))
                continue
        missing.append(StrengthEntry(user_id, None))
    rated.sort(key=lambda pair: pair[0], reverse=True)
    return [entry for _, entry in rated] + sorted(missing, key=lambda e: e.user_id)


# Progreso

@dataclass(frozen=True)
class ProgressEntry:
    user_id: int
    pct: float | None
    exercises: int = 0


def best_1rm_by_exercise(records: list[SetRecord]) -> dict[int, float]:
    best: dict[int, float] = {}
    for record in records:
        value = record.estimated_1rm
        if value is not None and value > best.get(record.exercise_id, 0):
            best[record.exercise_id] = value
    return best


def progress_table(records: list[SetRecord], user_ids: list[int], current: tuple[date, date],
                   baseline: tuple[date, date]) -> list[ProgressEntry]:
    grouped = by_user(records)
    entries = []
    for user_id in user_ids:
        mine = grouped.get(user_id, [])
        now = best_1rm_by_exercise(in_range(mine, *current))
        before = best_1rm_by_exercise(in_range(mine, *baseline))
        common = [e for e in now if e in before]
        changes = [100 * (now[e] / before[e] - 1) for e in common]
        entries.append(ProgressEntry(user_id, sum(changes) / len(changes) if changes else None, len(changes)))
    return sorted(entries, key=lambda e: (e.pct is None, -(e.pct or 0), e.user_id))


def progress_windows(start: date, end: date) -> tuple[tuple[date, date], tuple[date, date]]:
    """El último mes del período contra el mes anterior a que empiece."""
    return (month_start(end), end), (shift_months(start, -1), start - timedelta(days=1))


# Semana y constancia

def monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


def goal_in_force(changes: list[tuple[date, int]], week: date) -> int | None:
    current = None
    for start, goal in sorted(changes):
        if start <= week:
            current = goal
    return current


def training_days(records: list[SetRecord]) -> set[date]:
    return {r.date for r in records}


@dataclass(frozen=True)
class WeeklyEntry:
    user_id: int
    sessions: int
    goal: int | None
    status: str  # "done", "on" o "out"


def weekly_table(records: list[SetRecord], goals: dict[int, int | None], today: date) -> list[WeeklyEntry]:
    start = monday(today)
    grouped = by_user(in_range(records, start, start + timedelta(days=6)))
    entries = []
    for user_id, goal in goals.items():
        days = training_days(grouped.get(user_id, []))
        sessions = len(days)
        # Quedan los días después de hoy, más hoy si todavía no entrenó.
        free_days = 6 - today.weekday() + (0 if today in days else 1)
        if goal and sessions >= goal:
            status = "done"
        elif goal and goal - sessions > free_days:
            status = "out"
        else:
            status = "on"
        entries.append(WeeklyEntry(user_id, sessions, goal, status))
    return sorted(entries, key=lambda e: (-e.sessions, -(e.sessions / e.goal if e.goal else 0), e.user_id))


@dataclass(frozen=True)
class ConsistencyEntry:
    user_id: int
    pct: float | None
    streak: int = 0
    weeks: int = 0


def week_results(days: set[date], changes: list[tuple[date, int]], today: date) -> dict[date, bool]:
    """Para cada semana cerrada desde la primera sesión: si se llegó al objetivo vigente."""
    if not days:
        return {}
    results = {}
    week = monday(min(days))
    this_week = monday(today)
    while week < this_week:
        goal = goal_in_force(changes, week)
        if goal:
            count = sum(1 for d in days if week <= d <= week + timedelta(days=6))
            results[week] = count >= goal
        week += timedelta(days=7)
    return results


def consistency_table(records: list[SetRecord], goals: dict[int, list[tuple[date, int]]], start: date,
                      end: date, today: date) -> list[ConsistencyEntry]:
    grouped = by_user(records)
    entries = []
    for user_id, changes in goals.items():
        results = week_results(training_days(grouped.get(user_id, [])), changes, today)
        in_period = [met for week, met in results.items() if week >= monday(start) and week <= end]
        streak = 0
        for week in sorted(results, reverse=True):
            if not results[week]:
                break
            streak += 1
        pct = 100 * sum(in_period) / len(in_period) if in_period else None
        entries.append(ConsistencyEntry(user_id, pct, streak, len(in_period)))
    return sorted(entries, key=lambda e: (e.pct is None, -(e.pct or 0), -e.streak, e.user_id))
