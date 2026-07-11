import hard_mode


def test_normal_mode_is_identity():
    assert hard_mode.scale_hp(600, False) == 600
    assert hard_mode.scale_damage(2, False) == 2
    assert hard_mode.scale_spawn_probability(0.05, False) == 0.05
    assert hard_mode.scale_boss_cooldown(15000, False) == 15000
    assert hard_mode.scale_start_delay(3000, False) == 3000


def test_hard_hp_is_tripled():
    assert hard_mode.scale_hp(600, True) == 1800
    assert hard_mode.scale_hp(50000, True) == 150000


def test_hard_damage_is_tripled():
    assert hard_mode.scale_damage(2, True) == 6
    assert hard_mode.scale_damage(5, True) == 15


def test_hard_spawn_probability_is_doubled():
    assert hard_mode.scale_spawn_probability(0.05, True) == 0.10


def test_hard_boss_cooldown_is_halved_and_int():
    assert hard_mode.scale_boss_cooldown(15000, True) == 7500
    result = hard_mode.scale_boss_cooldown(700, True)
    assert result == 350
    assert isinstance(result, int)


def test_hard_start_delay_is_halved():
    assert hard_mode.scale_start_delay(3000, True) == 1500


def test_normal_mode_reward_scalers_apply_coin_multiplier():
    assert hard_mode.scale_clear_threshold(1000, False) == 1000
    assert hard_mode.scale_kill_score(2, False) == 2
    assert hard_mode.scale_coin(20, False) == 260


def test_hard_clear_threshold_is_doubled():
    assert hard_mode.scale_clear_threshold(1000, True) == 2000
    assert hard_mode.scale_clear_threshold(1810, True) == 3620


def test_hard_kill_score_is_1_5x_and_int():
    assert hard_mode.scale_kill_score(10, True) == 15
    result = hard_mode.scale_kill_score(2, True)
    assert result == 3
    assert isinstance(result, int)


def test_hard_coin_includes_normal_and_hard_multipliers():
    assert hard_mode.scale_coin(20, True) == 455
    result = hard_mode.scale_coin(30, True)
    assert result == 682
    assert isinstance(result, int)
