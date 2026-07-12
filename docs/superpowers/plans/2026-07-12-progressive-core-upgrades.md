# Progressive Core Upgrades Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Make core-upgrade gains increase per level and cap each later gain.

**Architecture:** A pure upgrade_scaling.py module provides all level math. main.py calls it for save restoration, UI next-gain text, and upgrade purchases, avoiding duplicate formulas.

**Tech Stack:** Python 3.12, Pygame 2.6.1, unittest, pytest.

## Global Constraints

- Damage and projectile speed cap each purchase gain at 30; hull capacity caps it at 5.
- At current level L, the next purchase gives min(L + 1, cap); all levels remain purchasable.
- Preserve costs, save schema, sentry upgrades, tactical support, score, and combat difficulty scaling.
- Rebuild saved core stats from bases damage 50, speed 20, and lives 10.
- Run commands from repo root with .\.venv\Scripts\python.exe.

---

### Task 1: Add pure progressive-upgrade math

**Files:**
- Create: upgrade_scaling.py
- Create: tests/test_upgrade_scaling.py

**Interfaces:**
- Produces: next_increment(current_level, cap) -> int
- Produces: cumulative_bonus(level, cap) -> int
- Produces: purchase_bonus(current_level, add_levels, cap) -> int
- Consumed by: main.py

- [ ] **Step 1: Write failing progression tests**

Create tests/test_upgrade_scaling.py:

~~~python
import unittest

import upgrade_scaling


class UpgradeScalingTests(unittest.TestCase):
    def test_next_increment_ramps_then_stays_at_cap(self):
        self.assertEqual(upgrade_scaling.next_increment(0, 30), 1)
        self.assertEqual(upgrade_scaling.next_increment(1, 30), 2)
        self.assertEqual(upgrade_scaling.next_increment(29, 30), 30)
        self.assertEqual(upgrade_scaling.next_increment(30, 30), 30)

    def test_damage_and_speed_cumulative_bonus_ramps_then_caps(self):
        self.assertEqual(upgrade_scaling.cumulative_bonus(0, 30), 0)
        self.assertEqual(upgrade_scaling.cumulative_bonus(1, 30), 1)
        self.assertEqual(upgrade_scaling.cumulative_bonus(30, 30), 465)
        self.assertEqual(upgrade_scaling.cumulative_bonus(31, 30), 495)

    def test_hull_bonus_ramps_to_five_then_stays_at_five_per_level(self):
        self.assertEqual(upgrade_scaling.cumulative_bonus(5, 5), 15)
        self.assertEqual(upgrade_scaling.cumulative_bonus(6, 5), 20)

    def test_batch_purchase_matches_sequential_increments(self):
        self.assertEqual(upgrade_scaling.purchase_bonus(28, 4, 30), 119)
        self.assertEqual(upgrade_scaling.purchase_bonus(3, 3, 5), 14)


if __name__ == "__main__":
    unittest.main()
~~~

- [ ] **Step 2: Run test to verify it fails**

Run:

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests\test_upgrade_scaling.py -q
~~~

Expected: collection failure because upgrade_scaling does not exist.

- [ ] **Step 3: Write minimal implementation**

Create upgrade_scaling.py:

~~~python
def _non_negative_int(value):
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def next_increment(current_level, cap):
    current_level = _non_negative_int(current_level)
    cap = _non_negative_int(cap)
    if cap == 0:
        return 0
    return min(current_level + 1, cap)


def cumulative_bonus(level, cap):
    level = _non_negative_int(level)
    cap = _non_negative_int(cap)
    if cap == 0:
        return 0
    ramp = min(level, cap)
    return ramp * (ramp + 1) // 2 + (level - ramp) * cap


def purchase_bonus(current_level, add_levels, cap):
    current_level = _non_negative_int(current_level)
    add_levels = _non_negative_int(add_levels)
    return (
        cumulative_bonus(current_level + add_levels, cap)
        - cumulative_bonus(current_level, cap)
    )
~~~

- [ ] **Step 4: Run focused tests to verify they pass**

Run:

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests\test_upgrade_scaling.py -q
~~~

Expected: 4 passed.

- [ ] **Step 5: Commit pure progression module**

~~~powershell
git add upgrade_scaling.py tests/test_upgrade_scaling.py
git commit -m "feat: add progressive upgrade scaling"
~~~

### Task 2: Integrate progressive math into saves, UI, and purchases

**Files:**
- Modify: main.py:6,164-179,342-368,413-450

**Interfaces:**
- Consumes: upgrade_scaling.next_increment, upgrade_scaling.cumulative_bonus, and upgrade_scaling.purchase_bonus.
- Produces: consistent saved, displayed, and purchased core-upgrade values.

- [ ] **Step 1: Integrate shared scaling in main.py**

Add near imports:

~~~python
import upgrade_scaling

CORE_DAMAGE_SPEED_CAP = 30
HULL_CAPACITY_CAP = 5
~~~

Replace flat saved-stat reconstruction with:

~~~python
max_lives = 10 + upgrade_scaling.cumulative_bonus(
    live_level,
    HULL_CAPACITY_CAP,
)
BULLET_SPEED = 20 + upgrade_scaling.cumulative_bonus(
    bullet_speed_level,
    CORE_DAMAGE_SPEED_CAP,
)
player.damage = 50 + upgrade_scaling.cumulative_bonus(
    damage_level,
    CORE_DAMAGE_SPEED_CAP,
)
~~~

In get_upgrade_rows, calculate three next values with next_increment and change the core subtitles:

~~~python
damage_next = upgrade_scaling.next_increment(
    damage_level,
    CORE_DAMAGE_SPEED_CAP,
)
speed_next = upgrade_scaling.next_increment(
    bullet_speed_level,
    CORE_DAMAGE_SPEED_CAP,
)
lives_next = upgrade_scaling.next_increment(
    live_level,
    HULL_CAPACITY_CAP,
)
~~~

~~~python
subtitle=f"COST {damage_level_need_coin:,} COINS\nCURRENT DMG {player.damage}  /  +{damage_next} DAMAGE"
subtitle=f"COST {bullet_speed_level_need_coin:,} COINS\nCURRENT SPD {BULLET_SPEED}  /  +{speed_next} SPEED"
subtitle=f"COST {live_level_need_coin:,} COINS  /  +{lives_next} LIFE"
~~~

Replace each flat core-upgrade stat addition with the corresponding delta:

~~~python
player.damage += upgrade_scaling.purchase_bonus(
    damage_level,
    add_levels,
    CORE_DAMAGE_SPEED_CAP,
)
BULLET_SPEED += upgrade_scaling.purchase_bonus(
    bullet_speed_level,
    add_levels,
    CORE_DAMAGE_SPEED_CAP,
)
max_lives += upgrade_scaling.purchase_bonus(
    live_level,
    add_levels,
    HULL_CAPACITY_CAP,
)
~~~

Keep the existing level increments, costs, support branches, autosave, and return values unchanged.

- [ ] **Step 2: Run focused tests and syntax check**

Run:

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests\test_upgrade_scaling.py -q
.\.venv\Scripts\python.exe -m py_compile main.py upgrade_scaling.py
~~~

Expected: 5 passed and no compile output.

- [ ] **Step 3: Run complete suite**

Run:

~~~powershell
.\.venv\Scripts\python.exe -m pytest -q
~~~

Expected: exit code 0 with no failures.

- [ ] **Step 4: Commit integration**

~~~powershell
git add main.py tests/test_upgrade_scaling.py upgrade_scaling.py
git commit -m "feat: scale core upgrade gains by level"
~~~
