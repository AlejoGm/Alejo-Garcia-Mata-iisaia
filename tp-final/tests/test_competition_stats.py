from datetime import date

from backend.stats import FaceOff, campaign_points, duel_result, head_to_head, imbalance
from tests.test_stats import rec

SEXES = {1: "M", 2: "M"}
START = date(2026, 10, 1)


def test_duel_absolute_winner_within_window():
    sets = [rec(100, 5, date(2026, 10, 2), user=1), rec(105, 3, date(2026, 10, 3), user=2),
            rec(200, 1, date(2026, 10, 9), user=1)]  # fuera del plazo de 7 días
    result = duel_result(sets, SEXES, 1, 2, exercise_id=1, mode="absolute", start=START, days=7, today=date(2026, 10, 10))
    assert result.winner == 2
    assert result.finished is True
    assert (result.challenger_value, result.opponent_value) == (100, 105)


def test_duel_dots_uses_bodyweight():
    sets = [rec(130, 1, date(2026, 10, 2), user=1, bw=65), rec(170, 1, date(2026, 10, 2), user=2, bw=95)]
    result = duel_result(sets, SEXES, 1, 2, exercise_id=1, mode="dots", start=START, days=7, today=date(2026, 10, 4))
    assert result.winner == 2
    assert result.finished is False


def test_duel_missing_data_loses_and_nobody_is_a_draw():
    sets = [rec(100, 5, date(2026, 10, 2), user=1)]
    assert duel_result(sets, SEXES, 1, 2, 1, "absolute", START, 3, date(2026, 10, 5)).winner == 1
    assert duel_result([], SEXES, 1, 2, 1, "absolute", START, 3, date(2026, 10, 5)).winner is None


def test_duel_exact_tie_is_a_draw():
    sets = [rec(100, 5, date(2026, 10, 2), user=1), rec(100, 5, date(2026, 10, 3), user=2)]
    assert duel_result(sets, SEXES, 1, 2, 1, "absolute", START, 7, date(2026, 10, 9)).winner is None


def test_imbalance_levels():
    assert imbalance(100, 95) == ("low", 0.05)
    assert imbalance(100, 80)[0] == "medium"
    assert imbalance(100, 70)[0] == "high"
    assert imbalance(None, 70) == ("none", None)


def test_campaign_points_like_f1_with_firsts_as_tiebreak():
    tables = [[1, 2, 3], [2, 1], [3]]
    standings = campaign_points(tables, [1, 2, 3, 4])
    assert [(e.user_id, e.points, e.firsts) for e in standings] == [(1, 18, 1), (2, 18, 1), (3, 16, 1), (4, 0, 0)]


def test_campaign_tie_on_points_and_firsts_keeps_user_order():
    standings = campaign_points([[1, 2], [2, 1]], [1, 2])
    assert [e.user_id for e in standings] == [1, 2]


# Cara a cara

def test_head_to_head_only_exercises_both_did_and_winner_by_dots():
    mine = [rec(100, 1, user=1, exercise=1, bw=90), rec(60, 5, user=1, exercise=2, bw=90),
            rec(50, 12, user=1, exercise=3)]
    theirs = [rec(90, 1, user=2, exercise=1, bw=60), rec(70, 5, user=2, exercise=2, bw=60), rec(40, 5, user=2, exercise=3)]

    result = head_to_head(mine, theirs, "M", "M")

    # El 3 no entra: yo no tengo 1RM estimable (12 reps).
    assert [f.exercise_id for f in result] == [1, 2]
    squat = result[0]
    assert (squat.mine_1rm, squat.theirs_1rm) == (100, 90)
    assert squat.winner == "theirs"  # 90 con 60 kg de peso vale más DOTS que 100 con 90
    assert result[1].winner == "theirs"
    assert isinstance(squat, FaceOff)


def test_head_to_head_tie():
    result = head_to_head([rec(100, 1, user=1)], [rec(100, 1, user=2)], "M", "M")
    assert result[0].winner == "tie"
