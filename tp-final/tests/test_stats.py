from datetime import date

import pytest

from backend.stats import SetRecord, estimate_1rm, strength_ranking

DAY = date(2026, 9, 20)


def record(member, exercise, weight, reps):
    return SetRecord(member=member, exercise=exercise, date=DAY, weight_kg=weight, reps=reps)


def test_one_rep_is_the_weight_itself():
    assert estimate_1rm(100, 1) == 100


def test_epley_for_several_reps():
    assert estimate_1rm(100, 5) == pytest.approx(116.67, abs=0.01)


def test_more_than_ten_reps_does_not_estimate():
    assert estimate_1rm(60, 11) is None


def test_ten_reps_still_estimates():
    assert estimate_1rm(60, 10) == pytest.approx(80)


def test_strength_divides_best_1rm_by_bodyweight():
    sets = [record("ana", "sentadilla", 100, 1), record("beto", "sentadilla", 120, 1)]
    ranking = strength_ranking(sets, {"ana": 50, "beto": 100}, ["sentadilla"])

    entries = ranking["sentadilla"]
    assert [e.member for e in entries] == ["ana", "beto"]
    assert entries[0].ratio == pytest.approx(2.0)
    assert entries[1].ratio == pytest.approx(1.2)


def test_strength_uses_the_best_set_of_each_member():
    sets = [record("ana", "banca", 40, 1), record("ana", "banca", 50, 1), record("ana", "banca", 45, 1)]
    ranking = strength_ranking(sets, {"ana": 50}, ["banca"])

    assert ranking["banca"][0].best_1rm == pytest.approx(50)


def test_sets_over_ten_reps_do_not_count_for_strength():
    sets = [record("ana", "banca", 40, 1), record("ana", "banca", 45, 15)]
    ranking = strength_ranking(sets, {"ana": 50}, ["banca"])

    assert ranking["banca"][0].best_1rm == pytest.approx(40)


def test_member_without_data_goes_last_as_no_data():
    sets = [record("beto", "banca", 60, 1)]
    ranking = strength_ranking(sets, {"ana": 50, "beto": 100}, ["banca"])

    entries = ranking["banca"]
    assert [e.member for e in entries] == ["beto", "ana"]
    assert entries[1].best_1rm is None
    assert entries[1].ratio is None


def test_only_sets_over_ten_reps_counts_as_no_data():
    sets = [record("ana", "banca", 40, 12)]
    ranking = strength_ranking(sets, {"ana": 50}, ["banca"])

    assert ranking["banca"][0].ratio is None


def test_exercises_outside_the_challenge_are_ignored():
    sets = [record("ana", "curl", 20, 1)]
    ranking = strength_ranking(sets, {"ana": 50}, ["banca"])

    assert list(ranking) == ["banca"]
    assert ranking["banca"][0].ratio is None
