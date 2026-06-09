import upgrade_selection


def test_basic_level_zero_cost_is_free():
    assert upgrade_selection.level_purchase_cost(1234, 0) == 0


def test_support_cost_uses_level_offset_one():
    assert upgrade_selection.level_purchase_cost(50_000, 0, level_offset=1) == 50_000
    assert upgrade_selection.level_purchase_cost(50_000, 3, level_offset=1) == 200_000


def test_batch_total_matches_sequential_level_costs():
    base_cost = 125
    current_level = 3
    add_levels = 5

    expected = sum(
        upgrade_selection.level_purchase_cost(base_cost, level)
        for level in range(current_level, current_level + add_levels)
    )

    assert (
        upgrade_selection.total_upgrade_cost(base_cost, current_level, add_levels)
        == expected
    )


def test_max_affordable_returns_highest_payable_basic_count():
    assert upgrade_selection.max_affordable_addition(100, 0, 0) == 1
    assert upgrade_selection.max_affordable_addition(100, 0, 299) == 2
    assert upgrade_selection.max_affordable_addition(100, 0, 300) == 3


def test_max_affordable_support_has_no_free_first_level():
    assert upgrade_selection.max_affordable_addition(100, 0, 0, level_offset=1) == 0
    assert upgrade_selection.max_affordable_addition(100, 0, 99, level_offset=1) == 0
    assert upgrade_selection.max_affordable_addition(100, 0, 100, level_offset=1) == 1
    assert upgrade_selection.max_affordable_addition(100, 0, 300, level_offset=1) == 2


def test_zero_base_cost_has_no_affordable_addition():
    assert upgrade_selection.max_affordable_addition(0, 0, 10_000) == 0


def test_clamp_accepts_int_like_values_and_clamps_to_range():
    assert upgrade_selection.clamp_addition("3", 5) == 3
    assert upgrade_selection.clamp_addition(2.9, 5) == 2
    assert upgrade_selection.clamp_addition(99, 5) == 5


def test_clamp_maps_invalid_and_negative_values_to_zero():
    assert upgrade_selection.clamp_addition("invalid", 5) == 0
    assert upgrade_selection.clamp_addition(None, 5) == 0
    assert upgrade_selection.clamp_addition(-2, 5) == 0
    assert upgrade_selection.clamp_addition(2, -5) == 0


def test_slider_value_maps_endpoints_and_rounds_midpoint_up():
    assert upgrade_selection.slider_value_from_x(20, 20, 100, 5) == 0
    assert upgrade_selection.slider_value_from_x(120, 20, 100, 5) == 5
    assert upgrade_selection.slider_value_from_x(70, 20, 100, 5) == 3
    assert upgrade_selection.slider_value_from_x(-100, 20, 100, 5) == 0
    assert upgrade_selection.slider_value_from_x(999, 20, 100, 5) == 5


def test_slider_x_maps_value_endpoints_and_clamps_values():
    assert upgrade_selection.slider_x_from_value(0, 20, 100, 5) == 20
    assert upgrade_selection.slider_x_from_value(5, 20, 100, 5) == 120
    assert upgrade_selection.slider_x_from_value(3, 20, 100, 5) == 80
    assert upgrade_selection.slider_x_from_value(-1, 20, 100, 5) == 20
    assert upgrade_selection.slider_x_from_value(99, 20, 100, 5) == 120


def test_slider_max_add_zero_stays_at_zero_and_track_left():
    assert upgrade_selection.slider_value_from_x(75, 20, 100, 0) == 0
    assert upgrade_selection.slider_x_from_value(4, 20, 100, 0) == 20
