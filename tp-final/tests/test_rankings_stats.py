from datetime import date

import pytest

from backend.stats import (
    consistency_table, period_range, progress_span, progress_table, strength_table, weekly_table,
)
from tests.test_stats import rec

SEXES = {1: "M", 2: "M", 3: "F"}


# Períodos

def test_month_period_is_that_calendar_month():
    assert period_range("month", today=date(2026, 10, 6), month="2026-09") == (date(2026, 9, 1), date(2026, 9, 30))


def test_six_and_twelve_months_end_in_current_month():
    today = date(2026, 10, 6)
    assert period_range("6m", today=today) == (date(2026, 5, 1), date(2026, 10, 31))
    assert period_range("12m", today=today) == (date(2025, 11, 1), date(2026, 10, 31))


def test_all_starts_at_first_session_month_and_custom_uses_bounds():
    today = date(2026, 10, 6)
    assert period_range("all", today=today, first=date(2026, 3, 17)) == (date(2026, 3, 1), date(2026, 10, 31))
    assert period_range("custom", today=today, start="2026-01", end="2026-02") == (date(2026, 1, 1), date(2026, 2, 28))


def test_invalid_period_raises_value_error():
    with pytest.raises(ValueError):
        period_range("custom", today=date(2026, 10, 6), start="2026-05", end="2026-01")
    with pytest.raises(ValueError):
        period_range("month", today=date(2026, 10, 6), month="2026-13")


# Fuerza

def test_dots_ranking_puts_lighter_but_relatively_stronger_first():
    sets = [rec(170, 1, user=1, bw=95), rec(130, 1, user=2, bw=65)]
    table = strength_table(sets, SEXES, exercise_id=1, mode="dots")
    assert [e.user_id for e in table] == [1, 2, 3]
    assert table[0].value == pytest.approx(107.1, abs=0.05)
    assert table[2].value is None


def test_absolute_ranking_breaks_ties_with_reps():
    sets = [rec(100, 3, user=1), rec(100, 5, user=2), rec(90, 10, user=3)]
    table = strength_table(sets, SEXES, exercise_id=1, mode="absolute")
    assert [(e.user_id, e.reps) for e in table] == [(2, 5), (1, 3), (3, 10)]


def test_strength_ignores_other_exercises():
    sets = [rec(100, 1, user=1, exercise=2)]
    assert strength_table(sets, SEXES, exercise_id=1, mode="absolute")[0].value is None


# Progreso

SEP = (date(2026, 9, 1), date(2026, 9, 30))
AUG = (date(2026, 8, 1), date(2026, 8, 31))


def test_progress_compares_best_1rm_of_both_months_and_averages_exercises():
    sets = [
        rec(100, 1, date(2026, 8, 10), user=1, exercise=1), rec(110, 1, date(2026, 9, 10), user=1, exercise=1),
        rec(50, 1, date(2026, 8, 10), user=1, exercise=2), rec(50, 1, date(2026, 9, 10), user=1, exercise=2),
    ]
    table = progress_table(sets, [1, 2], current=SEP, baseline=AUG)
    assert table[0].user_id == 1
    assert table[0].pct == pytest.approx(5.0)  # (+10% + 0%) / 2
    assert table[0].exercises == 2
    assert table[1].pct is None


def test_progress_skips_exercises_missing_in_one_month():
    sets = [rec(100, 1, date(2026, 8, 10), user=1), rec(120, 1, date(2026, 9, 10), user=1, exercise=2)]
    assert progress_table(sets, [1], current=SEP, baseline=AUG)[0].pct is None


# Semana

MON = date(2026, 10, 5)


def test_weekly_counts_distinct_days_and_marks_done():
    sets = [rec(100, 1, MON, user=1), rec(100, 1, MON, user=1, session=99), rec(100, 1, date(2026, 10, 6), user=1)]
    table = weekly_table(sets, {1: 2, 2: 3}, today=date(2026, 10, 7))
    assert (table[0].user_id, table[0].sessions, table[0].status) == (1, 2, "done")


def test_weekly_out_when_remaining_days_cannot_reach_goal():
    saturday = date(2026, 10, 10)
    sets = [rec(100, 1, MON, user=1)]
    table = weekly_table(sets, {1: 4}, today=saturday)
    assert table[0].status == "out"  # faltan 3 y quedan sábado y domingo


def test_weekly_today_already_trained_does_not_count_as_free_day():
    saturday = date(2026, 10, 10)
    sets = [rec(100, 1, MON, user=1), rec(100, 1, saturday, user=1)]
    assert weekly_table(sets, {1: 4}, today=saturday)[0].status == "out"  # faltan 2 y queda solo el domingo
    assert weekly_table(sets, {1: 3}, today=saturday)[0].status == "on"


def test_weekly_orders_by_sessions_then_goal_ratio():
    sets = [rec(1, 1, MON, user=1), rec(1, 1, MON, user=2)]
    table = weekly_table(sets, {1: 4, 2: 2}, today=MON)
    assert [e.user_id for e in table] == [2, 1]


# Constancia

def test_consistency_pct_and_streak_over_closed_weeks():
    goals = {1: [(date(2026, 9, 7), 2)]}
    weeks = [date(2026, 9, 7), date(2026, 9, 14), date(2026, 9, 21), date(2026, 9, 28)]
    met = {date(2026, 9, 7): 2, date(2026, 9, 14): 1, date(2026, 9, 21): 2, date(2026, 9, 28): 3}
    sets = []
    for week in weeks:
        for offset in range(met[week]):
            sets.append(rec(100, 1, date.fromordinal(week.toordinal() + offset), user=1))
    table = consistency_table(sets, goals, start=date(2026, 9, 1), end=date(2026, 10, 31), today=date(2026, 10, 6))
    entry = table[0]
    assert entry.weeks == 4          # la semana del 5/10 está en curso y no cuenta
    assert entry.pct == pytest.approx(75.0)
    assert entry.streak == 2


def test_consistency_uses_goal_in_force_each_week():
    goals = {1: [(date(2026, 9, 7), 1), (date(2026, 9, 14), 3)]}
    sets = [rec(100, 1, date(2026, 9, 8), user=1), rec(100, 1, date(2026, 9, 15), user=1)]
    table = consistency_table(sets, goals, start=date(2026, 9, 1), end=date(2026, 9, 20), today=date(2026, 10, 6))
    assert table[0].pct == pytest.approx(50.0)


def test_consistency_ignores_weeks_before_first_session_and_no_data_goes_last():
    goals = {1: [(date(2026, 8, 3), 1)], 2: [(date(2026, 8, 3), 1)]}
    sets = [rec(100, 1, date(2026, 9, 22), user=1)]
    table = consistency_table(sets, goals, start=date(2026, 9, 1), end=date(2026, 9, 30), today=date(2026, 10, 6))
    assert table[0].user_id == 1
    assert table[0].weeks == 2  # semanas del 21/9 y del 28/9
    assert table[1].pct is None


def test_first_goal_also_applies_to_sessions_logged_before_it():
    goals = {1: [(date(2026, 9, 28), 1)]}
    sets = [rec(100, 1, date(2026, 9, 8), user=1), rec(100, 1, date(2026, 9, 15), user=1)]
    table = consistency_table(sets, goals, start=date(2026, 9, 1), end=date(2026, 9, 20), today=date(2026, 10, 6))
    assert table[0].weeks == 2
    assert table[0].pct == pytest.approx(100.0)


def test_progress_span_compares_first_and_last_month_with_data_in_the_period():
    sets = [rec(100, 1, date(2026, 6, 10), user=1), rec(105, 1, date(2026, 8, 10), user=1),
            rec(110, 1, date(2026, 10, 2), user=1), rec(80, 1, date(2026, 9, 1), user=2)]
    table = progress_span(sets, [1, 2], start=date(2026, 5, 1), end=date(2026, 10, 31))
    assert table[0].user_id == 1
    assert table[0].pct == pytest.approx(10.0)
    assert table[1].pct is None  # un solo mes con datos
