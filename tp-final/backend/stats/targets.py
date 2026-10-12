"""Objetivo para PR: las series más chicas que la regla de PRs cuenta como récord."""
from dataclasses import dataclass

from backend.stats.core import MAX_REPS_FOR_1RM, SetRecord, best_1rm, best_absolute, estimate_1rm

MAX_REPS = 50


@dataclass(frozen=True)
class PRTarget:
    kind: str  # "reps" o "weight"
    weight_kg: float
    reps: int


def pr_targets(records: list[SetRecord], step: float) -> list[PRTarget]:
    """Más reps con tu mejor carga, o un salto más de peso con las reps justas para superar tu mejor 1RM."""
    best = best_absolute(records)
    if best is None or best.bodyweight_exercise:
        return []
    targets = []
    if best.reps < MAX_REPS:
        targets.append(PRTarget("reps", best.load, best.reps + 1))
    heavier = round(best.load + step, 2)
    top = best_1rm(records)
    if top is None:
        reps = best.reps
    else:
        # Siempre hay una: con 10 reps, la carga más pesada supera cualquier 1RM de una carga menor.
        reps = next(r for r in range(1, MAX_REPS_FOR_1RM + 1) if estimate_1rm(heavier, r) > top.estimated_1rm)
    targets.append(PRTarget("weight", heavier, reps))
    return targets
