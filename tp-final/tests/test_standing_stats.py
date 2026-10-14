import pytest

from backend.stats import Standing, set_for_1rm, standing


def test_first_set_of_the_month_enters_the_table():
    result = standing({2: 100, 3: 80}, me=1, new_value=90)
    assert result == Standing(position_before=None, position=2, total=3, passed=[3], next_id=2)


def test_passing_two_and_chasing_the_next():
    values = {1: 70, 2: 120, 3: 95, 4: 80, 5: 60}
    result = standing(values, me=1, new_value=100)
    assert (result.position_before, result.position) == (4, 2)
    assert result.passed == [3, 4]  # del que estaba más arriba al de más abajo
    assert result.next_id == 2


def test_a_worse_set_keeps_my_best_of_the_month():
    result = standing({1: 100, 2: 90}, me=1, new_value=80)
    assert (result.position_before, result.position, result.passed, result.next_id) == (1, 1, [], None)


def test_tie_shares_the_place_and_counts_as_passed_only_when_strictly_above():
    tie = standing({2: 90}, me=1, new_value=90)
    assert (tie.position, tie.passed, tie.next_id) == (1, [], None)
    above = standing({1: 90, 2: 90}, me=1, new_value=91)
    assert (above.position_before, above.position, above.passed) == (1, 1, [2])


def test_no_value_for_the_set_keeps_the_previous_standing():
    result = standing({1: 80, 2: 90}, me=1, new_value=None)
    assert (result.position_before, result.position, result.next_id) == (2, 2, 2)


def test_set_for_1rm_inverts_epley():
    assert set_for_1rm(120, 6) == pytest.approx(100)
    assert set_for_1rm(100, 1) == 100
