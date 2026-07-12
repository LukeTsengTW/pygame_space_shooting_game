import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from upgrade_scaling import _non_negative_int, cumulative_bonus, next_increment, purchase_bonus


MAIN_PATH = Path(__file__).parents[1] / "main.py"
PLAYER_PATH = Path(__file__).parents[1] / "player.py"


def load_main_function(name: str, namespace: dict) -> tuple:
    """Compile one main.py function without running its pygame game loop."""
    tree = ast.parse(MAIN_PATH.read_text(encoding="utf-8"), filename=str(MAIN_PATH))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
    compiled = compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), str(MAIN_PATH), "exec")
    exec(compiled, namespace)
    return namespace[name], namespace


def load_player_method(name: str, namespace: dict) -> tuple:
    """Compile one Player method without loading Pygame assets or audio."""
    tree = ast.parse(PLAYER_PATH.read_text(encoding="utf-8"), filename=str(PLAYER_PATH))
    player_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Player")
    method = next(node for node in player_class.body if isinstance(node, ast.FunctionDef) and node.name == name)
    compiled = compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(PLAYER_PATH), "exec")
    exec(compiled, namespace)
    return namespace[name], namespace


def test_core_upgrade_increment_caps_match_upgrade_page_limits() -> None:
    tree = ast.parse(MAIN_PATH.read_text(encoding="utf-8"), filename=str(MAIN_PATH))
    constants = {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tree.body
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in {"CORE_DAMAGE_SPEED_CAP", "HULL_CAPACITY_CAP"}
        )
    }

    assert constants["CORE_DAMAGE_SPEED_CAP"] == 5
    assert constants["HULL_CAPACITY_CAP"] == 3


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


@pytest.mark.parametrize("value", [None, "corrupt", float("nan"), float("inf"), float("-inf")])
def test_upgrade_math_sanitizes_corrupt_values(value: object) -> None:
    assert _non_negative_int(value) == 0


def test_apply_save_state_rebuilds_core_stats_with_progressive_bonuses() -> None:
    player = SimpleNamespace()
    namespace = {
        "player": player,
        "pygame": SimpleNamespace(mixer=SimpleNamespace(music=SimpleNamespace(set_volume=lambda _: None))),
        "config": SimpleNamespace(BULLET_SPEED=20),
        "upgrade_scaling": __import__("upgrade_scaling"),
        "CORE_DAMAGE_SPEED_CAP": 5,
        "HULL_CAPACITY_CAP": 3,
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

    assert namespace["max_lives"] == 25
    assert namespace["config"].BULLET_SPEED == 160
    assert player.damage == 195
    assert player.lives == 25


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
        "config": SimpleNamespace(BULLET_SPEED=485),
        "support_upgrades": support_upgrades,
        "upgrade_scaling": __import__("upgrade_scaling"),
        "CORE_DAMAGE_SPEED_CAP": 5,
        "HULL_CAPACITY_CAP": 3,
    }
    get_upgrade_rows, _ = load_main_function("get_upgrade_rows", namespace)
    rows = {row["key"]: row for row in get_upgrade_rows()}

    assert "+5 DAMAGE" in rows["damage"]["subtitle"]
    assert "+5 SPEED" in rows["bullet_speed"]["subtitle"]
    assert "+3 LIFE" in rows["lives"]["subtitle"]


@pytest.mark.parametrize(
    ("upgrade_key", "level_name", "stat_name", "current_level", "add_levels", "cap"),
    [
        ("damage", "damage_level", "damage", 28, 1, 5),
        ("damage", "damage_level", "damage", 28, 3, 5),
        ("bullet_speed", "bullet_speed_level", "BULLET_SPEED", 28, 1, 5),
        ("bullet_speed", "bullet_speed_level", "BULLET_SPEED", 28, 3, 5),
        ("lives", "live_level", "max_lives", 3, 1, 3),
        ("lives", "live_level", "max_lives", 3, 3, 3),
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
        "config": SimpleNamespace(BULLET_SPEED=20),
        "max_lives": 10,
        "upgrade_scaling": __import__("upgrade_scaling"),
        "CORE_DAMAGE_SPEED_CAP": 5,
        "HULL_CAPACITY_CAP": 3,
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
    if stat_name == "damage":
        starting_stat = player.damage
    elif stat_name == "BULLET_SPEED":
        starting_stat = namespace["config"].BULLET_SPEED
    else:
        starting_stat = namespace[stat_name]

    assert buy_upgrade_levels(upgrade_key, add_levels) is True
    if stat_name == "damage":
        ending_stat = player.damage
    elif stat_name == "BULLET_SPEED":
        ending_stat = namespace["config"].BULLET_SPEED
    else:
        ending_stat = namespace[stat_name]
    assert ending_stat == starting_stat + purchase_bonus(current_level, add_levels, cap)
    assert namespace[level_name] == current_level + add_levels
    assert player.lives == 2


def test_player_firing_path_reads_projectile_speed_from_config() -> None:
    class Vector:
        def __init__(self, x: int, y: int) -> None:
            self.x = x
            self.y = y

        def rotate(self, _angle: int) -> "Vector":
            return self

    class SpriteGroup:
        def __init__(self) -> None:
            self.sprites = []

        def add(self, sprite: object) -> None:
            self.sprites.append(sprite)

    bullets = SpriteGroup()
    all_sprites = SpriteGroup()
    namespace = {
        "BULLET_SPEED": 20,
        "config": SimpleNamespace(BULLET_SPEED=485),
        "pygame": SimpleNamespace(
            K_UP="up",
            K_DOWN="down",
            K_LEFT="left",
            K_RIGHT="right",
            time=SimpleNamespace(get_ticks=lambda: 100),
            math=SimpleNamespace(Vector2=Vector),
        ),
        "player_bullet_angle": (0,),
        "PLAYER_SPEED": 4,
        "SCREEN_WIDTH": 600,
        "SCREEN_HEIGHT": 900,
        "GAMEPLAY_TOP": 80,
        "bullets": bullets,
        "all_sprites": all_sprites,
        "Bullet": lambda _player: SimpleNamespace(velocity=None),
    }
    update, _ = load_player_method("update", namespace)
    player = SimpleNamespace(
        out_of_game=False,
        control=0,
        rect=SimpleNamespace(left=1, right=10, top=100, bottom=200),
        last_shot_time=0,
    )

    update(player, {"up": False, "down": False, "left": False, "right": False}, (0, 0))

    assert bullets.sprites[0].velocity.y == -485
