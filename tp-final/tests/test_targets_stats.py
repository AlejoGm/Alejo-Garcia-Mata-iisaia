import pytest

from backend.stats import PRTarget, detect_prs, pr_targets
from tests.test_stats import D1, D2, rec


def test_no_history_has_no_target():
    assert pr_targets([], step=2.5) == []


def test_bodyweight_exercise_has_no_target():
    assert pr_targets([rec(10, 8, bodyweight_exercise=True)], step=2.5) == []


def test_one_more_rep_or_one_more_plate_with_reps_to_beat_the_1rm():
    # 80×8 → 1RM 101,3. Con 82,5 kg hacen falta 7 reps para superarlo.
    assert pr_targets([rec(80, 8), rec(70, 10)], step=2.5) == [PRTarget("reps", 80, 9), PRTarget("weight", 82.5, 7)]


def test_heavier_target_beats_a_1rm_from_a_lighter_set():
    # El mejor absoluto es 100×1, pero el mejor 1RM es 90×8 (114).
    targets = pr_targets([rec(100, 1), rec(90, 8, day=D2)], step=2.5)
    assert targets == [PRTarget("reps", 100, 2), PRTarget("weight", 102.5, 4)]


def test_without_an_estimable_1rm_keeps_the_reps():
    assert pr_targets([rec(60, 15)], step=2.5)[1] == PRTarget("weight", 62.5, 15)


def test_no_more_reps_target_past_the_limit():
    assert pr_targets([rec(20, 50)], step=2.5) == [PRTarget("weight", 22.5, 50)]


def test_step_in_pounds():
    assert pr_targets([rec(80, 8)], step=5 * 0.45359237)[1].weight_kg == pytest.approx(82.27, abs=0.01)


@pytest.mark.parametrize("target", pr_targets([rec(80, 8, day=D1)], step=2.5))
def test_every_target_counts_as_a_pr(target):
    history = [rec(80, 8, day=D1)]
    attempt = rec(target.weight_kg, target.reps, day=D2)
    assert attempt.set_id in detect_prs(history + [attempt])
