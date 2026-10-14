"""Posición en vivo: cómo queda uno en el grupo con una serie que todavía no guardó."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Standing:
    position_before: int | None
    position: int | None
    total: int
    passed: list[int]
    next_id: int | None


def place(values: dict[int, float], me: int, mine: float) -> int:
    """1 más los que tienen un valor estrictamente mayor: un empate comparte el lugar."""
    return 1 + sum(1 for uid, value in values.items() if uid != me and value > mine)


def standing(values: dict[int, float], me: int, new_value: float | None) -> Standing:
    """`values`: el mejor del mes de cada miembro con datos. Mi valor queda en el mayor entre el mío y la serie."""
    before = values.get(me)
    candidates = [v for v in (before, new_value) if v is not None]
    after = max(candidates) if candidates else None
    others = {uid: value for uid, value in values.items() if uid != me}
    if after is None:
        return Standing(None, None, len(others), [], None)
    passed = sorted((uid for uid, value in others.items() if (before is None or value >= before) and value < after),
                    key=lambda uid: -others[uid])
    above = [uid for uid, value in others.items() if value > after]
    return Standing(
        position_before=place(values, me, before) if before is not None else None,
        position=place(values, me, after),
        total=len(others) + 1,
        passed=passed,
        next_id=min(above, key=lambda uid: others[uid]) if above else None,
    )


def set_for_1rm(one_rm: float, reps: int) -> float:
    """Inversa de Epley: el peso que, a esas reps, da ese 1RM estimado."""
    return one_rm if reps == 1 else one_rm / (1 + reps / 30)
