"""Cuentas del panel del grupo."""


def volume(records):
    raise NotImplementedError


def session_count(records):
    raise NotImplementedError


def weekly_activity(records, today, weeks=8):
    raise NotImplementedError


def day_activity(records, today):
    raise NotImplementedError


def goal_progress(records, goals, today):
    raise NotImplementedError


DayActivity = WeekActivity = None
