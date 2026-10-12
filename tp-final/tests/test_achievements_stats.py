from datetime import date, timedelta

from backend.stats import achievements
from tests.test_stats import rec

LIFTS = {"bench": 10, "squat": 11, "deadlift": 12}
MON = date(2026, 9, 7)  # lunes
TODAY = date(2026, 10, 12)


def earned(records, changes=None, today=TODAY):
    return {a.key: a.day for a in achievements(records, changes or [], LIFTS, today)}


def test_nothing_without_sessions():
    assert achievements([], [], LIFTS, TODAY) == []


def test_first_session_and_session_counts_use_distinct_days():
    days = [MON + timedelta(days=i) for i in range(12)]
    records = [rec(50, 5, day=d) for d in days] + [rec(50, 5, day=days[0])]  # dos sesiones el primer día
    result = earned(records)
    assert result["first"] == days[0]
    assert result["sessions_10"] == days[9]
    assert "sessions_50" not in result


def test_streak_counts_consecutive_closed_weeks_meeting_the_goal():
    # Cuatro semanas con 2 días cada una, objetivo 2: la racha llega a 4 el domingo de la cuarta.
    records = [rec(50, 5, day=MON + timedelta(weeks=w, days=d)) for w in range(4) for d in (0, 2)]
    result = earned(records, changes=[(MON, 2)])
    assert result["streak_4"] == MON + timedelta(weeks=3, days=6)
    assert "streak_12" not in result


def test_a_missed_week_resets_the_streak():
    weeks = [0, 1, 2, 4, 5, 6]
    records = [rec(50, 5, day=MON + timedelta(weeks=w)) for w in weeks]
    assert "streak_4" not in earned(records, changes=[(MON, 1)])


def test_ten_prs_on_the_day_of_the_tenth():
    days = [MON + timedelta(days=i) for i in range(11)]
    records = [rec(50 + i, 5, day=d) for i, d in enumerate(days)]  # la primera es línea base
    assert earned(records)["prs_10"] == days[10]


def test_strength_relative_to_that_days_bodyweight():
    records = [
        rec(75, 3, day=MON, exercise=10, bw=80),             # banca 75 con 80 de peso: no
        rec(80, 1, day=MON + timedelta(days=2), exercise=10, bw=80),
        rec(120, 1, day=MON, exercise=11, bw=80),            # sentadilla 1,5× = 120
        rec(150, 1, day=MON, exercise=12, bw=80),            # peso muerto 2× = 160: no
    ]
    result = earned(records)
    assert result["bench_bw"] == MON + timedelta(days=2)
    assert result["squat_1_5"] == MON
    assert "deadlift_2" not in result


def test_ton_is_ten_thousand_kg_in_one_session():
    light = [rec(100, 10, day=MON, session=1) for _ in range(9)]
    heavy = [rec(100, 10, day=MON + timedelta(days=1), session=2) for _ in range(10)]
    assert earned(light + heavy)["ton"] == MON + timedelta(days=1)


def test_results_follow_the_catalog_order():
    keys = [a.key for a in achievements([rec(200, 1, day=MON, exercise=12, bw=80)], [], LIFTS, TODAY)]
    assert keys == ["first", "deadlift_2"]
