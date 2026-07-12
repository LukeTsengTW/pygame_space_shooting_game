import pytest

from upgrade_scaling import cumulative_bonus, next_increment, purchase_bonus


@pytest.mark.parametrize(
    ("current_level", "cap", "expected"),
    [
        (0, 30, 1),
        (1, 30, 2),
        (29, 30, 30),
        (30, 30, 30),
        (0, 0, 0),
    ],
)
def test_next_increment_caps_each_purchase(
    current_level: int, cap: int, expected: int
) -> None:
    assert next_increment(current_level, cap) == expected


@pytest.mark.parametrize(
    ("level", "cap", "expected"),
    [
        (0, 30, 0),
        (1, 30, 1),
        (30, 30, 465),
        (31, 30, 495),
        (5, 5, 15),
        (6, 5, 20),
    ],
)
def test_cumulative_bonus_ramps_then_uses_the_cap(
    level: int, cap: int, expected: int
) -> None:
    assert cumulative_bonus(level, cap) == expected


@pytest.mark.parametrize(
    ("current_level", "add_levels", "cap", "expected"),
    [
        (28, 4, 30, 119),
        (3, 3, 5, 14),
    ],
)
def test_purchase_bonus_returns_the_bonus_for_only_the_new_levels(
    current_level: int, add_levels: int, cap: int, expected: int
) -> None:
    assert purchase_bonus(current_level, add_levels, cap) == expected


@pytest.mark.parametrize(
    ("current_level", "add_levels", "cap", "expected"),
    [
        (-1, 1, 30, 1),
        (1, -1, 30, 0),
        (1, 1, -30, 0),
    ],
)
def test_upgrade_math_sanitizes_negative_values(
    current_level: int, add_levels: int, cap: int, expected: int
) -> None:
    assert purchase_bonus(current_level, add_levels, cap) == expected
