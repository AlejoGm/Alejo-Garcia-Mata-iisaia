from datetime import date, timedelta

import pytest

from backend.stats import bodyweight_series, monthly_series, muscle_sets, training_calendar, weekly_series
from tests.test_stats import rec


def test_monthly_best_and_average_of_session_bests():
    sets = [
        rec(100, 1, date(2026, 9, 2), session=1), rec(90, 1, date(2026, 9, 2), session=1),
        rec(110, 1, date(2026, 9, 9), session=2),
        rec(120, 1, date(2026, 10, 1), session=3),
    ]
    series = monthly_series(sets, exercise_id=1, start=date(2026, 8, 1), end=date(2026, 10, 31))
    assert [(p.month, p.best, p.average) for p in series] == [
        (date(2026, 8, 1), None, None), (date(2026, 9, 1), 110, 105), (date(2026, 10, 1), 120, 120),
    ]


def test_monthly_ignores_sets_over_ten_reps():
    series = monthly_series([rec(60, 12, date(2026, 9, 2))], 1, date(2026, 9, 1), date(2026, 9, 30))
    assert series[0].best is None


def test_weekly_best_per_monday():
    sets = [rec(100, 1, date(2026, 9, 1)), rec(105, 1, date(2026, 9, 3)), rec(102, 1, date(2026, 9, 8))]
    series = weekly_series(sets, 1, date(2026, 9, 1), date(2026, 9, 13))
    assert [(p.week, p.best) for p in series] == [(date(2026, 8, 31), 105), (date(2026, 9, 7), 102)]


def test_bodyweight_takes_last_session_of_each_week():
    sets = [rec(1, 1, date(2026, 9, 1), session=1, bw=80), rec(1, 1, date(2026, 9, 4), session=2, bw=79.5),
            rec(1, 1, date(2026, 9, 9), session=3, bw=79)]
    series = bodyweight_series(sets, date(2026, 9, 1), date(2026, 9, 13))
    assert [(p.week, p.kg) for p in series] == [(date(2026, 8, 31), 79.5), (date(2026, 9, 7), 79)]


def test_series_values_are_rounded_to_one_decimal():
    series = monthly_series([rec(100, 5, date(2026, 9, 2))], 1, date(2026, 9, 1), date(2026, 9, 30))
    assert series[0].best == pytest.approx(116.7)


# Calendario

def test_calendar_counts_sets_per_day_within_26_weeks():
    today = date(2026, 10, 14)  # miércoles; la semana arranca el lunes 12
    first_monday = date(2026, 4, 20)  # 25 semanas antes
    records = [rec(50, 5, day=today), rec(50, 5, day=today), rec(60, 5, day=date(2026, 10, 1)),
               rec(60, 5, day=first_monday), rec(60, 5, day=first_monday - timedelta(days=1))]

    days = training_calendar(records, today)

    assert [(d.day, d.sets) for d in days] == [(first_monday, 1), (date(2026, 10, 1), 1), (today, 2)]


# Series por músculo

def test_muscle_sets_average_closed_weeks_and_this_week():
    today = date(2026, 10, 14)  # semana del lunes 12
    muscles = {1: "Pecho", 2: "Espalda"}
    records = [
        rec(80, 5, day=date(2026, 10, 13), exercise=1), rec(80, 5, day=date(2026, 10, 13), exercise=1),
        *[rec(80, 5, day=date(2026, 10, 5), exercise=1) for _ in range(4)],    # semana anterior: 4
        *[rec(60, 8, day=date(2026, 9, 21), exercise=2) for _ in range(8)],    # hace 3 semanas: 8
        rec(60, 8, day=date(2026, 9, 7), exercise=2),                          # fuera de las 4 semanas
        rec(20, 10, day=date(2026, 10, 13), exercise=9),                        # sin músculo: Otros
    ]

    result = muscle_sets(records, muscles, today)

    assert [(m.muscle, m.this_week, m.average) for m in result] == [
        ("Espalda", 0, 2.0), ("Pecho", 2, 1.0), ("Otros", 1, 0.0)]
