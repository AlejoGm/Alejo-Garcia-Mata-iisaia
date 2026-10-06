"""Series para los gráficos personales."""


def monthly_series(records, exercise_id, start, end):
    raise NotImplementedError


def weekly_series(records, exercise_id, start, end):
    raise NotImplementedError


def bodyweight_series(records, start, end):
    raise NotImplementedError


BodyweightPoint = MonthPoint = WeekPoint = None
