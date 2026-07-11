# Normal Coin Multiplier Design

## Goal

Increase every enemy-kill coin reward in normal mode to three times its current value.

## Scope

Keep `ENEMY_REWARD_CONFIG` as the source of base reward values. Apply the mode multiplier only in `hard_mode.scale_coin`, which is already used by normal bullet kills and tactical-support kills.

## Behavior

- Normal mode returns `round(base_coin * NORMAL_COIN_MULTIPLIER)`, where `NORMAL_COIN_MULTIPLIER` is `3`.
- Hard mode returns `round(base_coin * NORMAL_COIN_MULTIPLIER * HARD_COIN_MULTIPLIER)`.
- `HARD_COIN_MULTIPLIER` remains `1.75`; hard rewards are therefore 5.25 times the pre-change base values.
- Score, enemy health, damage, spawn rates, item-drop rates, and base reward configuration remain unchanged.

## Tests

Extend `tests/test_hard_mode.py` with normal and hard reward assertions. Verify normal `20` becomes `60`, hard `20` becomes `105`, and the fractional result `30 * 3 * 1.75` rounds to `158`.
