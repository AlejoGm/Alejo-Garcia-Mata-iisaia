from datetime import date, timedelta


def monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


def goal_for_week(changes: list[tuple[date, int]], week: date) -> int | None:
    """Objetivo vigente en la semana que arranca el lunes `week`."""
    current = None
    for start, goal in sorted(changes):
        if start <= week:
            current = goal
    return current
