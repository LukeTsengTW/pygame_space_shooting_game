import math


def _non_negative_int(value):
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def level_purchase_cost(base_cost, level, level_offset=0):
    base_cost = _non_negative_int(base_cost)
    level = _non_negative_int(level)
    level_offset = _non_negative_int(level_offset)
    return base_cost * (level + level_offset)


def total_upgrade_cost(base_cost, current_level, add_levels, level_offset=0):
    base_cost = _non_negative_int(base_cost)
    current_level = _non_negative_int(current_level)
    add_levels = _non_negative_int(add_levels)
    level_offset = _non_negative_int(level_offset)
    first_level = current_level + level_offset
    return base_cost * add_levels * (2 * first_level + add_levels - 1) // 2


def max_affordable_addition(base_cost, current_level, budget, level_offset=0):
    base_cost = _non_negative_int(base_cost)
    current_level = _non_negative_int(current_level)
    budget = _non_negative_int(budget)
    level_offset = _non_negative_int(level_offset)
    if base_cost == 0:
        return 0

    low = 0
    high = 1
    while (
        total_upgrade_cost(base_cost, current_level, high, level_offset)
        <= budget
    ):
        low = high
        high *= 2

    while low + 1 < high:
        middle = (low + high) // 2
        if (
            total_upgrade_cost(base_cost, current_level, middle, level_offset)
            <= budget
        ):
            low = middle
        else:
            high = middle

    return low


def clamp_addition(value, max_add):
    return min(_non_negative_int(value), _non_negative_int(max_add))


def slider_value_from_x(mouse_x, track_left, track_width, max_add):
    max_add = _non_negative_int(max_add)
    if max_add == 0:
        return 0

    try:
        track_width = float(track_width)
        position = (float(mouse_x) - float(track_left)) / track_width
    except (TypeError, ValueError, ZeroDivisionError):
        return 0

    position = min(1.0, max(0.0, position))
    return min(max_add, math.floor(position * max_add + 0.5))


def slider_x_from_value(value, track_left, track_width, max_add):
    max_add = _non_negative_int(max_add)
    try:
        track_left = float(track_left)
        track_width = float(track_width)
    except (TypeError, ValueError):
        return 0

    if max_add == 0:
        return track_left

    value = clamp_addition(value, max_add)
    return track_left + track_width * value / max_add
