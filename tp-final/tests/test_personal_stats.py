from datetime import date

import pytest

from backend.stats import bodyweight_series, monthly_series, weekly_series
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
