from datetime import date

import pytest

from backend.stats import day_activity, goal_progress, session_count, volume, weekly_activity
from tests.test_stats import rec

WED = date(2026, 10, 7)  # semana del lunes 5/10


def test_volume_is_load_times_reps_including_bodyweight():
    sets = [rec(100, 5), rec(10, 8, bw=80, bodyweight_exercise=True)]
    assert volume(sets) == pytest.approx(500 + 90 * 8)


def test_sessions_are_distinct_user_and_day():
    sets = [rec(1, 1, WED, user=1, session=1), rec(1, 1, WED, user=1, session=2), rec(1, 1, WED, user=2)]
    assert session_count(sets) == 2


def test_weekly_activity_covers_eight_weeks_oldest_first():
    sets = [rec(100, 5, date(2026, 10, 5), user=1), rec(50, 10, date(2026, 9, 29), user=2)]
    series = weekly_activity(sets, today=WED, weeks=8)
    assert len(series) == 8
    assert series[-1].week == date(2026, 10, 5)
    assert (series[-1].sessions, series[-1].volume) == (1, 500)
    assert (series[-2].sessions, series[-2].volume) == (1, 500)
    assert series[0].week == date(2026, 8, 17)
    assert series[0].sessions == 0


def test_day_activity_counts_distinct_members_per_day():
    sets = [rec(1, 1, date(2026, 10, 5), user=1), rec(1, 1, date(2026, 10, 5), user=2),
            rec(1, 1, date(2026, 10, 5), user=2, session=99), rec(1, 1, date(2026, 10, 7), user=1)]
    days = day_activity(sets, today=WED)
    assert [d.members for d in days] == [2, 0, 1, 0, 0, 0, 0]
    assert days[0].day == date(2026, 10, 5)


def test_goal_progress_caps_each_member_at_their_goal():
    sets = [rec(1, 1, date(2026, 10, d), user=1) for d in (5, 6, 7)] + [rec(1, 1, date(2026, 10, 5), user=2)]
    # el 1 hizo 3 de 2 (cuenta 2), el 2 hizo 1 de 3: (2 + 1) / (2 + 3)
    assert goal_progress(sets, {1: 2, 2: 3, 3: None}, today=WED) == pytest.approx(60.0)


def test_goal_progress_without_goals_is_none():
    assert goal_progress([], {1: None}, today=WED) is None
