"""Pure calculations for progressively scaled player upgrades."""


def _non_negative_int(value: int) -> int:
    """Convert an upgrade value to a non-negative integer."""
    return max(0, int(value))


def next_increment(current_level: int, cap: int) -> int:
    """Return the bonus granted by the next purchase at *current_level*."""
    level = _non_negative_int(current_level)
    maximum = _non_negative_int(cap)
    if maximum == 0:
        return 0
    return min(level + 1, maximum)


def cumulative_bonus(level: int, cap: int) -> int:
    """Return the total bonus earned after *level* purchased levels."""
    purchased_levels = _non_negative_int(level)
    maximum = _non_negative_int(cap)
    ramp = min(purchased_levels, maximum)
    return ramp * (ramp + 1) // 2 + (purchased_levels - ramp) * maximum


def purchase_bonus(current_level: int, add_levels: int, cap: int) -> int:
    """Return the total bonus for the levels included in one purchase."""
    level = _non_negative_int(current_level)
    added_levels = _non_negative_int(add_levels)
    return cumulative_bonus(level + added_levels, cap) - cumulative_bonus(level, cap)
