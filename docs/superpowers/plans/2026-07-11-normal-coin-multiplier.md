# Normal Coin Multiplier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every normal-mode enemy kill award three times its configured base coin reward, while hard mode applies its existing 1.75 multiplier after that increase.

**Architecture:** `main.py` continues to pass base rewards in `ENEMY_REWARD_CONFIG` through `hard_mode.scale_coin`. The pure scaler owns normal multiplier, so bullet and tactical-support kills use identical rewards without touching combat logic.

**Tech Stack:** Python 3.12, pytest, Pygame 2.6.1.

## Global Constraints

- Preserve `ENEMY_REWARD_CONFIG` base coin values in `main.py`.
- Normal rewards use multiplier `3`; hard rewards use `3 * 1.75` and Python `round()`.
- Do not alter score, health, damage, spawn-rate, delay, cooldown, or item-drop scaling.
- Run commands from repository root with `.\.venv\Scripts\python.exe`.

---

### Task 1: Scale normal and hard coin rewards

**Files:**
- Modify: `tests/test_hard_mode.py:37-40,55-59`
- Modify: `hard_mode.py:5-12,43-44`
- Test: `tests/test_hard_mode.py`

**Interfaces:**
- Consumes: `scale_coin(coin, hard)` called by `main.py` with base values from `ENEMY_REWARD_CONFIG`.
- Produces: `scale_coin(coin, False) -> int` equal to `round(coin * 3)` and `scale_coin(coin, True) -> int` equal to `round(coin * 3 * 1.75)`.

- [ ] **Step 1: Write failing reward tests**

Replace coin assertion in `test_normal_mode_reward_scalers_are_identity` and replace `test_hard_coin_is_1_75x_and_int` with:

```python
def test_normal_mode_reward_scalers_apply_coin_multiplier():
    assert hard_mode.scale_clear_threshold(1000, False) == 1000
    assert hard_mode.scale_kill_score(2, False) == 2
    assert hard_mode.scale_coin(20, False) == 60


def test_hard_coin_includes_normal_and_hard_multipliers():
    assert hard_mode.scale_coin(20, True) == 105
    result = hard_mode.scale_coin(30, True)
    assert result == 158
    assert isinstance(result, int)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hard_mode.py -q
```

Expected: FAIL because normal `scale_coin(20, False)` returns `20` and hard `scale_coin(20, True)` returns `35` before implementation.

- [ ] **Step 3: Add normal coin multiplier and compose multipliers**

In `hard_mode.py`, add constant beside reward multipliers and replace `scale_coin` with:

```python
NORMAL_COIN_MULTIPLIER = 3
HARD_COIN_MULTIPLIER = 1.75


def scale_coin(coin, hard):
    multiplier = NORMAL_COIN_MULTIPLIER
    if hard:
        multiplier *= HARD_COIN_MULTIPLIER
    return round(coin * multiplier)
```

- [ ] **Step 4: Run focused tests to verify they pass**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hard_mode.py -q
```

Expected: `10 passed`.

- [ ] **Step 5: Run complete test suite**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: exit code `0`; no test failures.

- [ ] **Step 6: Commit implementation**

```powershell
git add hard_mode.py tests/test_hard_mode.py
git commit -m "feat: triple normal enemy coin rewards"
```
