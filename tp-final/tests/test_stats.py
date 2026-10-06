from datetime import date

import pytest

from backend.stats import SetRecord, best_absolute, detect_prs, dots, estimate_1rm

D1, D2, D3 = date(2026, 9, 1), date(2026, 9, 8), date(2026, 9, 15)

_ids = iter(range(1, 10_000))


def rec(weight, reps, day=D1, user=1, exercise=1, session=None, bw=80.0, bodyweight_exercise=False, position=0):
    set_id = next(_ids)
    return SetRecord(set_id=set_id, session_id=session or set_id, user_id=user, exercise_id=exercise, date=day,
                     weight_kg=weight, reps=reps, bodyweight_kg=bw, bodyweight_exercise=bodyweight_exercise,
                     position=position)


# 1RM

def test_one_rep_is_the_load_itself():
    assert estimate_1rm(100, 1) == 100


def test_epley_for_several_reps():
    assert estimate_1rm(100, 5) == pytest.approx(116.67, abs=0.01)


def test_ten_reps_still_estimates_but_eleven_does_not():
    assert estimate_1rm(60, 10) == pytest.approx(80)
    assert estimate_1rm(60, 11) is None


def test_bodyweight_exercise_load_adds_bodyweight():
    assert rec(10, 1, bw=80, bodyweight_exercise=True).load == 90
    assert rec(10, 1, bw=80).load == 10


# DOTS

def test_dots_matches_hand_computed_values():
    assert dots(170, 95, "M") == pytest.approx(107.1, abs=0.05)
    assert dots(130, 65, "M") == pytest.approx(103.0, abs=0.05)


def test_dots_uses_female_coefficients():
    assert dots(100, 60, "F") == pytest.approx(dots(100, 60, "F"))
    assert dots(100, 60, "F") > dots(100, 60, "M")


def test_dots_clamps_bodyweight_to_formula_range():
    assert dots(100, 30, "M") == dots(100, 40, "M")
    assert dots(100, 250, "M") == dots(100, 210, "M")
    assert dots(100, 180, "F") == dots(100, 150, "F")


# Absoluto

def test_best_absolute_prefers_load_then_reps_then_earliest():
    first = rec(100, 3, D1)
    assert best_absolute([rec(95, 10, D1), first, rec(100, 2, D2)]) is first
    later_more_reps = rec(100, 5, D3)
    assert best_absolute([first, later_more_reps]) is later_more_reps
    same_later = rec(100, 3, D2)
    assert best_absolute([same_later, first]) is first


# PRs

def test_first_set_of_an_exercise_is_not_a_pr():
    s = rec(100, 5, D1)
    assert detect_prs([s]) == {}


def test_weight_pr_and_1rm_pr():
    base = rec(110, 1, D1)
    rep_pr = rec(100, 8, D2)      # sube el 1RM (126.7) pero no el peso
    weight_pr = rec(112, 1, D3)
    assert detect_prs([base, rep_pr, weight_pr]) == {rep_pr.set_id: "1rm", weight_pr.set_id: "weight"}


def test_same_weight_more_reps_is_weight_pr():
    base = rec(100, 3, D1)
    more = rec(100, 5, D2)
    assert detect_prs([base, more])[more.set_id] == "weight"


def test_weight_pr_wins_when_both_apply():
    base = rec(100, 5, D1)
    both = rec(105, 5, D2)
    assert detect_prs([base, both]) == {both.set_id: "weight"}


def test_sets_in_one_session_compare_against_previous_ones():
    s1 = rec(100, 1, D1, session=7, position=0)
    s2 = rec(105, 1, D1, session=7, position=1)
    s3 = rec(102, 1, D1, session=7, position=2)
    assert detect_prs([s3, s2, s1]) == {s2.set_id: "weight"}


def test_prs_are_per_user_and_exercise():
    a = rec(100, 1, D1, user=1)
    b = rec(120, 1, D2, user=2)
    c = rec(50, 1, D2, user=1, exercise=2)
    assert detect_prs([a, b, c]) == {}


def test_more_than_ten_reps_can_be_weight_pr_but_not_1rm_pr():
    base = rec(60, 12, D1)
    heavier = rec(62, 12, D2)
    assert detect_prs([base, heavier]) == {heavier.set_id: "weight"}
