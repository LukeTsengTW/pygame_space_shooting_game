import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from upgrade_scaling import cumulative_bonus, next_increment, purchase_bonus


MAIN_PATH = Path(__file__).parents[1] / "main.py"


def load_main_function(name: str, namespace: dict) -> tuple:
    """Compile one main.py function without running its pygame game loop."""
    tree = ast.parse(MAIN_PATH.read_text(encoding="utf-8"), filename=str(MAIN_PATH))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
    compiled = compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), str(MAIN_PATH), "exec")
    exec(compiled, namespace)
    return namespace[name], namespace


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


def test_apply_save_state_rebuilds_core_stats_with_progressive_bonuses() -> None:
    player = SimpleNamespace()
    namespace = {
        "player": player,
        "pygame": SimpleNamespace(mixer=SimpleNamespace(music=SimpleNamespace(set_volume=lambda _: None))),
        "upgrade_scaling": __import__("upgrade_scaling"),
        "CORE_DAMAGE_SPEED_CAP": 30,
        "HULL_CAPACITY_CAP": 5,
    }
    apply_save_state, namespace = load_main_function("apply_save_state", namespace)

    apply_save_state(
        {
            "progression": {"highest_unlocked_level": 4, "is_complete_game": False, "hard_level": 1},
            "economy": {
                "coin": 500,
                "damage_level": 31,
                "bullet_speed_level": 30,
                "live_level": 6,
                "sentry_gun_level": 2,
                "tactical_support_level": 3,
            },
            "settings": {"control_mode": 1, "volume_level": 0.5, "opening_seen": True},
        }
    )

    assert namespace["max_lives"] == 30
    assert namespace["BULLET_SPEED"] == 485
    assert player.damage == 545
    assert player.lives == 30


def test_core_upgrade_rows_show_the_level_scaled_next_gain() -> None:
    support_upgrades = SimpleNamespace(
        SENTRY_GUN_BASE_COST=1,
        TACTICAL_SUPPORT_BASE_COST=1,
        next_upgrade_cost=lambda *_: 1,
        sentry_gun_stats=lambda _: {"count": 1, "lives": 1, "damage": 1, "bullet_speed": 1, "shot_interval_ms": 1},
        tactical_support_stats=lambda _: {"trigger_ratio": 0.5, "cooldown_ms": 1000},
    )
    namespace = {
        "damage_level": 30,
        "bullet_speed_level": 30,
        "live_level": 5,
        "damage_level_need_coin": 1,
        "bullet_speed_level_need_coin": 1,
        "live_level_need_coin": 1,
        "sentry_gun_level": 0,
        "tactical_support_level": 0,
        "player": SimpleNamespace(damage=515),
        "BULLET_SPEED": 485,
        "support_upgrades": support_upgrades,
        "upgrade_scaling": __import__("upgrade_scaling"),
        "CORE_DAMAGE_SPEED_CAP": 30,
        "HULL_CAPACITY_CAP": 5,
    }
    get_upgrade_rows, _ = load_main_function("get_upgrade_rows", namespace)
    rows = {row["key"]: row for row in get_upgrade_rows()}

    assert "+30 DAMAGE" in rows["damage"]["subtitle"]
    assert "+30 SPEED" in rows["bullet_speed"]["subtitle"]
    assert "+5 LIFE" in rows["lives"]["subtitle"]


@pytest.mark.parametrize(
    ("upgrade_key", "level_name", "stat_name", "current_level", "add_levels", "cap"),
    [
        ("damage", "damage_level", "damage", 28, 1, 30),
        ("damage", "damage_level", "damage", 28, 3, 30),
        ("bullet_speed", "bullet_speed_level", "BULLET_SPEED", 28, 1, 30),
        ("bullet_speed", "bullet_speed_level", "BULLET_SPEED", 28, 3, 30),
        ("lives", "live_level", "max_lives", 3, 1, 5),
        ("lives", "live_level", "max_lives", 3, 3, 5),
    ],
)
def test_batched_core_purchase_uses_progressive_bonus(
    upgrade_key: str,
    level_name: str,
    stat_name: str,
    current_level: int,
    add_levels: int,
    cap: int,
) -> None:
    player = SimpleNamespace(coin=1_000, damage=50, lives=2, out_of_game=False)
    namespace = {
        "player": player,
        "damage_level": current_level if level_name == "damage_level" else 0,
        "bullet_speed_level": current_level if level_name == "bullet_speed_level" else 0,
        "live_level": current_level if level_name == "live_level" else 0,
        "damage_level_need_coin": 0,
        "bullet_speed_level_need_coin": 0,
        "live_level_need_coin": 0,
        "sentry_gun_level": 0,
        "tactical_support_level": 0,
        "BULLET_SPEED": 20,
        "max_lives": 10,
        "upgrade_scaling": __import__("upgrade_scaling"),
        "CORE_DAMAGE_SPEED_CAP": 30,
        "HULL_CAPACITY_CAP": 5,
        "upgrade_selection": SimpleNamespace(
            clamp_addition=lambda amount, _: amount,
            total_upgrade_cost=lambda *_: 1,
        ),
        "get_upgrade_rows": lambda: (
            {"key": "damage", "cost_base": 1234, "level": namespace["damage_level"], "level_offset": 0},
            {"key": "bullet_speed", "cost_base": 321, "level": namespace["bullet_speed_level"], "level_offset": 0},
            {"key": "lives", "cost_base": 5432, "level": namespace["live_level"], "level_offset": 0},
        ),
        "autosave": lambda: None,
    }
    buy_upgrade_levels, namespace = load_main_function("buy_upgrade_levels", namespace)
    starting_stat = getattr(player, "damage") if stat_name == "damage" else namespace[stat_name]

    assert buy_upgrade_levels(upgrade_key, add_levels) is True
    ending_stat = getattr(player, "damage") if stat_name == "damage" else namespace[stat_name]
    assert ending_stat == starting_stat + purchase_bonus(current_level, add_levels, cap)
    assert namespace[level_name] == current_level + add_levels
    assert player.lives == 2
