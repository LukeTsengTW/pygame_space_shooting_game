# Upgrade Level Selector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace immediate one-level UPGRADE purchases with the approved tactical modal for selecting and buying an affordable number of added levels.

**Architecture:** Put all pricing, affordability, clamping, and slider conversion in a new pygame-free `upgrade_selection.py` module. Keep drawing and geometry in `ui.py`, while `main.py` owns modal state, keyboard/mouse event routing, and one atomic batch transaction followed by one autosave.

**Tech Stack:** Python 3.12, Pygame 2.6.1, `unittest`, existing tactical UI helpers, existing autosave system.

---

## File Structure

- Create `upgrade_selection.py`: pure pricing, affordability, input clamping, and integer slider mapping.
- Create `tests/test_upgrade_selection.py`: unit coverage for all pure selection rules.
- Modify `ui.py`: modal layout and rendering only; no upgrade-state mutation.
- Modify `tests/test_ui.py`: modal geometry and rendering tests under dummy SDL.
- Modify `main.py`: upgrade metadata, modal state, input handling, and atomic batch purchase.

Do not import `main.py` from tests because importing it launches the game.

### Task 1: Add Pure Upgrade Selection Calculations

**Files:**
- Create: `upgrade_selection.py`
- Create: `tests/test_upgrade_selection.py`

- [ ] **Step 1: Write failing pricing and affordability tests**

Create `tests/test_upgrade_selection.py`:

```python
import unittest

from upgrade_selection import (
    clamp_addition,
    level_purchase_cost,
    max_affordable_addition,
    slider_value_from_x,
    slider_x_from_value,
    total_upgrade_cost,
)


class UpgradeSelectionTests(unittest.TestCase):
    def test_basic_upgrade_preserves_free_level_zero_purchase(self):
        self.assertEqual(level_purchase_cost(1234, 0), 0)
        self.assertEqual(level_purchase_cost(1234, 1), 1234)

    def test_support_upgrade_starts_at_base_price(self):
        self.assertEqual(level_purchase_cost(50_000, 0, level_offset=1), 50_000)
        self.assertEqual(level_purchase_cost(50_000, 1, level_offset=1), 100_000)

    def test_batch_total_matches_sequential_prices(self):
        sequential = sum(level_purchase_cost(1234, level) for level in range(3, 8))
        self.assertEqual(total_upgrade_cost(1234, 3, 5), sequential)
        self.assertEqual(total_upgrade_cost(50_000, 0, 2, level_offset=1), 150_000)

    def test_max_affordable_addition_returns_highest_payable_value(self):
        self.assertEqual(max_affordable_addition(1234, 0, 0), 1)
        self.assertEqual(max_affordable_addition(1234, 0, 1233), 1)
        self.assertEqual(max_affordable_addition(1234, 0, 1234), 2)
        self.assertEqual(max_affordable_addition(50_000, 0, 149_999, level_offset=1), 1)
        self.assertEqual(max_affordable_addition(50_000, 0, 150_000, level_offset=1), 2)

    def test_zero_coins_cannot_buy_support_upgrade(self):
        self.assertEqual(max_affordable_addition(50_000, 0, 0, level_offset=1), 0)
        self.assertEqual(max_affordable_addition(70_000, 4, 0, level_offset=1), 0)

    def test_clamp_addition_accepts_int_like_values_and_rejects_invalid_values(self):
        self.assertEqual(clamp_addition(-3, 8), 0)
        self.assertEqual(clamp_addition("5", 8), 5)
        self.assertEqual(clamp_addition(99, 8), 8)
        self.assertEqual(clamp_addition("", 8), 0)
        self.assertEqual(clamp_addition("not-a-number", 8), 0)

    def test_slider_mapping_handles_endpoints_and_rounding(self):
        self.assertEqual(slider_value_from_x(100, 100, 200, 8), 0)
        self.assertEqual(slider_value_from_x(300, 100, 200, 8), 8)
        self.assertEqual(slider_value_from_x(212, 100, 200, 8), 4)
        self.assertEqual(slider_x_from_value(0, 100, 200, 8), 100)
        self.assertEqual(slider_x_from_value(8, 100, 200, 8), 300)
        self.assertEqual(slider_x_from_value(4, 100, 200, 8), 200)

    def test_slider_mapping_is_safe_when_no_level_is_affordable(self):
        self.assertEqual(slider_value_from_x(250, 100, 200, 0), 0)
        self.assertEqual(slider_x_from_value(7, 100, 200, 0), 100)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests and verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_upgrade_selection -v
```

Expected: `ERROR` because `upgrade_selection` does not exist.

- [ ] **Step 3: Implement the pure calculation module**

Create `upgrade_selection.py`:

```python
def _non_negative_int(value):
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
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
    if add_levels == 0:
        return 0

    first_multiplier = current_level + level_offset
    last_multiplier = first_multiplier + add_levels - 1
    return base_cost * add_levels * (first_multiplier + last_multiplier) // 2


def max_affordable_addition(base_cost, current_level, coins, level_offset=0):
    coins = _non_negative_int(coins)
    if _non_negative_int(base_cost) == 0:
        return 0

    low = 0
    high = 1
    while total_upgrade_cost(
        base_cost,
        current_level,
        high,
        level_offset,
    ) <= coins:
        low = high
        high *= 2

    while low + 1 < high:
        middle = (low + high) // 2
        if total_upgrade_cost(
            base_cost,
            current_level,
            middle,
            level_offset,
        ) <= coins:
            low = middle
        else:
            high = middle
    return low


def clamp_addition(value, max_add):
    max_add = _non_negative_int(max_add)
    return min(max_add, _non_negative_int(value))


def slider_value_from_x(mouse_x, track_left, track_width, max_add):
    track_width = _non_negative_int(track_width)
    max_add = _non_negative_int(max_add)
    if track_width == 0 or max_add == 0:
        return 0

    ratio = (mouse_x - track_left) / track_width
    ratio = max(0.0, min(1.0, ratio))
    return round(ratio * max_add)


def slider_x_from_value(value, track_left, track_width, max_add):
    track_width = _non_negative_int(track_width)
    max_add = _non_negative_int(max_add)
    value = clamp_addition(value, max_add)
    if track_width == 0 or max_add == 0:
        return track_left
    return track_left + round(track_width * value / max_add)
```

The exponential search followed by binary search keeps affordability
calculation fast even if a save contains an unusually large coin value.

- [ ] **Step 4: Run the pure tests and verify they pass**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_upgrade_selection -v
```

Expected: 8 tests pass.

- [ ] **Step 5: Commit the pure selection logic**

```powershell
git add upgrade_selection.py tests/test_upgrade_selection.py
git commit -m "feat: add upgrade batch selection calculations"
```

### Task 2: Add Tactical Modal Geometry and Rendering

**Files:**
- Modify: `ui.py` after `draw_modal_backdrop`
- Modify: `tests/test_ui.py`

- [ ] **Step 1: Write failing modal geometry and rendering tests**

Add these imports in `tests/test_ui.py`:

```python
    draw_upgrade_level_modal,
    upgrade_level_modal_rects,
```

Add to `TacticalUiGeometryTests`:

```python
    def test_upgrade_level_modal_controls_are_in_bounds_and_separated(self):
        rects = upgrade_level_modal_rects(600, 900)
        screen_rect = pygame.Rect(0, 0, 600, 900)

        self.assertTrue(screen_rect.contains(rects["modal"]))
        for name, rect in rects.items():
            if name != "modal":
                self.assertTrue(rects["modal"].contains(rect), name)

        self.assertFalse(rects["minus"].colliderect(rects["slider"]))
        self.assertFalse(rects["slider"].colliderect(rects["plus"]))
        self.assertFalse(rects["cancel"].colliderect(rects["confirm"]))
        self.assertFalse(rects["current"].colliderect(rects["projected"]))
```

Add to `TacticalUiRenderingTests`:

```python
    def test_upgrade_level_modal_renders_approved_controls(self):
        controls = draw_upgrade_level_modal(
            self.surface,
            "WEAPON DAMAGE",
            current_level=3,
            selected_add=9,
            max_add=9,
            total_cost=66_651,
            input_text="9",
            input_active=True,
            mouse_pos=(0, 0),
        )

        self.assertEqual(
            set(controls),
            {
                "modal",
                "current",
                "projected",
                "input",
                "minus",
                "slider",
                "slider_thumb",
                "plus",
                "cost",
                "cancel",
                "confirm",
            },
        )
        self.assertNotEqual(
            self.surface.get_at(controls["modal"].center),
            pygame.Color(0, 0, 0, 0),
        )
        self.assertEqual(controls["slider_thumb"].centerx, controls["slider"].right)

    def test_upgrade_level_modal_disables_controls_at_zero(self):
        controls = draw_upgrade_level_modal(
            self.surface,
            "SENTRY GUN",
            current_level=0,
            selected_add=0,
            max_add=0,
            total_cost=0,
            input_text="0",
            input_active=False,
            mouse_pos=(0, 0),
        )

        self.assertEqual(controls["slider_thumb"].centerx, controls["slider"].left)
        self.assertTrue(controls["modal"].contains(controls["confirm"]))
```

- [ ] **Step 2: Run the UI tests and verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_ui -v
```

Expected: import errors for the two new UI helpers.

- [ ] **Step 3: Add modal layout and rendering helpers**

Add near `draw_modal_backdrop` in `ui.py`:

```python
def upgrade_level_modal_rects(screen_width, screen_height):
    modal = pygame.Rect(92, 145, min(416, screen_width - 40), 610)
    modal.centerx = screen_width // 2
    modal.centery = screen_height // 2
    return {
        "modal": modal,
        "current": pygame.Rect(modal.left + 28, modal.top + 92, 166, 68),
        "projected": pygame.Rect(modal.left + 222, modal.top + 92, 166, 68),
        "input": pygame.Rect(modal.centerx - 64, modal.top + 205, 128, 52),
        "minus": pygame.Rect(modal.left + 28, modal.top + 302, 54, 54),
        "slider": pygame.Rect(modal.left + 102, modal.top + 324, 212, 10),
        "plus": pygame.Rect(modal.right - 82, modal.top + 302, 54, 54),
        "cost": pygame.Rect(modal.left + 28, modal.top + 400, modal.width - 56, 72),
        "cancel": pygame.Rect(modal.left + 28, modal.bottom - 82, 166, 54),
        "confirm": pygame.Rect(modal.right - 194, modal.bottom - 82, 166, 54),
    }


def draw_upgrade_level_modal(
    surface,
    title,
    *,
    current_level,
    selected_add,
    max_add,
    total_cost,
    input_text,
    input_active,
    mouse_pos,
):
    from upgrade_selection import slider_x_from_value

    controls = upgrade_level_modal_rects(surface.get_width(), surface.get_height())
    modal = draw_modal_backdrop(surface, controls["modal"])
    controls["modal"] = modal

    draw_text(surface, title, 25, COLORS["text"], (modal.centerx, modal.top + 37))
    pygame.draw.line(
        surface,
        COLORS["cyan"],
        (modal.left + 82, modal.top + 66),
        (modal.right - 82, modal.top + 66),
        2,
    )
    draw_stat_card(
        surface,
        controls["current"],
        "Current level",
        f"LV. {current_level}",
        accent=COLORS["cyan"],
    )
    draw_stat_card(
        surface,
        controls["projected"],
        "After upgrade",
        f"LV. {current_level + selected_add}",
        accent=COLORS["gold"],
    )

    draw_text(
        surface,
        "LEVELS TO ADD",
        11,
        COLORS["muted"],
        (modal.centerx, controls["input"].top - 15),
    )
    input_border = COLORS["cyan_hover"] if input_active else COLORS["border"]
    draw_panel(
        surface,
        controls["input"],
        fill=COLORS["navy"],
        border=input_border,
        alpha=248,
        cut=6,
    )
    shown_input = input_text if input_active else f"+{selected_add}"
    draw_text(surface, shown_input or "0", 23, COLORS["text"], controls["input"].center)

    draw_button(
        surface,
        controls["minus"],
        "-",
        hovered=controls["minus"].collidepoint(mouse_pos) and selected_add > 0,
        disabled=selected_add <= 0,
    )
    draw_button(
        surface,
        controls["plus"],
        "+",
        hovered=controls["plus"].collidepoint(mouse_pos) and selected_add < max_add,
        style="primary",
        disabled=selected_add >= max_add,
    )

    slider = controls["slider"]
    pygame.draw.rect(
        surface,
        COLORS["track"],
        slider,
        border_radius=slider.height // 2,
    )
    thumb_x = slider_x_from_value(
        selected_add,
        slider.left,
        slider.width,
        max_add,
    )
    if thumb_x > slider.left:
        fill = slider.copy()
        fill.width = thumb_x - slider.left
        pygame.draw.rect(
            surface,
            COLORS["cyan"],
            fill,
            border_radius=slider.height // 2,
        )
    thumb = pygame.Rect(0, 0, 28, 28)
    thumb.center = (thumb_x, slider.centery)
    pygame.draw.circle(surface, COLORS["panel"], thumb.center, 14)
    pygame.draw.circle(surface, COLORS["cyan_hover"], thumb.center, 14, 4)
    controls["slider_thumb"] = thumb
    draw_text(
        surface,
        "+0",
        11,
        COLORS["muted"],
        (slider.left, slider.bottom + 18),
        anchor="midleft",
    )
    draw_text(
        surface,
        f"MAX +{max_add}",
        11,
        COLORS["muted"],
        (slider.right, slider.bottom + 18),
        anchor="midright",
    )

    draw_panel(
        surface,
        controls["cost"],
        fill=COLORS["navy"],
        border=COLORS["border"],
        alpha=248,
        cut=7,
        border_width=1,
    )
    draw_text(
        surface,
        "TOTAL UPGRADE COST",
        10,
        COLORS["muted"],
        (controls["cost"].centerx, controls["cost"].top + 20),
    )
    draw_text(
        surface,
        f"{total_cost:,} COINS",
        22,
        COLORS["gold"],
        (controls["cost"].centerx, controls["cost"].bottom - 22),
    )

    draw_button(
        surface,
        controls["cancel"],
        "CANCEL",
        hovered=controls["cancel"].collidepoint(mouse_pos),
    )
    draw_button(
        surface,
        controls["confirm"],
        "CONFIRM",
        hovered=controls["confirm"].collidepoint(mouse_pos) and selected_add > 0,
        style="primary",
        disabled=selected_add <= 0,
    )
    return controls
```

- [ ] **Step 4: Run UI tests and verify they pass**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_ui -v
```

Expected: all UI tests pass.

- [ ] **Step 5: Commit the modal UI**

```powershell
git add ui.py tests/test_ui.py
git commit -m "feat: add tactical upgrade selection modal"
```

### Task 3: Add Upgrade Metadata and Atomic Batch Purchase

**Files:**
- Modify: `main.py` imports, `get_upgrade_rows()`, and `buy_upgrade()`

- [ ] **Step 1: Import pure helpers and the modal renderer**

Add:

```python
import upgrade_selection
```

Add this name as its own line inside the existing `from ui import (` block:

```python
    draw_upgrade_level_modal,
```

- [ ] **Step 2: Extend every upgrade row with batch pricing metadata**

In `get_upgrade_rows()`, add `cost_base` and `level_offset` to every row:

```python
        {
            "key": "damage",
            "label": "WEAPON DAMAGE",
            "level": damage_level,
            "cost": damage_level_need_coin,
            "cost_base": 1234,
            "level_offset": 0,
            "subtitle": (
                f"COST {damage_level_need_coin:,} COINS\n"
                f"CURRENT DMG {player.damage}  /  +1 DAMAGE"
            ),
        },
```

Use:

```python
("bullet_speed", 321, 0)
("lives", 5432, 0)
("sentry", support_upgrades.SENTRY_GUN_BASE_COST, 1)
("tactical", support_upgrades.TACTICAL_SUPPORT_BASE_COST, 1)
```

Keep the existing `cost` and `subtitle` fields so the store rows continue to
show the next one-level price and current stats.

- [ ] **Step 3: Replace one-level mutation with an atomic batch transaction**

Replace `buy_upgrade(upgrade_key)` with:

```python
def buy_upgrade_levels(upgrade_key, add_levels):
    global BULLET_SPEED, max_lives
    global damage_level, bullet_speed_level, live_level
    global damage_level_need_coin, bullet_speed_level_need_coin, live_level_need_coin
    global sentry_gun_level, tactical_support_level

    rows = {row["key"]: row for row in get_upgrade_rows()}
    row = rows[upgrade_key]
    add_levels = upgrade_selection.clamp_addition(add_levels, add_levels)
    if add_levels <= 0:
        return False

    total_cost = upgrade_selection.total_upgrade_cost(
        row["cost_base"],
        row["level"],
        add_levels,
        row["level_offset"],
    )
    if player.coin < total_cost:
        return False

    player.coin -= total_cost
    if upgrade_key == "damage":
        damage_level += add_levels
        player.damage += add_levels
        damage_level_need_coin = damage_level * 1234
    elif upgrade_key == "bullet_speed":
        bullet_speed_level += add_levels
        BULLET_SPEED += add_levels
        bullet_speed_level_need_coin = bullet_speed_level * 321
    elif upgrade_key == "lives":
        live_level += add_levels
        max_lives += add_levels
        live_level_need_coin = live_level * 5432
    elif upgrade_key == "sentry":
        sentry_gun_level += add_levels
        if not player.out_of_game:
            spawn_sentry_guns()
    elif upgrade_key == "tactical":
        tactical_support_level += add_levels
    else:
        return False

    autosave()
    return True
```

Do not loop over one-level purchases. The single transaction must deduct once,
spawn sentries at most once, and autosave once.

- [ ] **Step 4: Syntax-check the transaction integration**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile main.py upgrade_selection.py
```

Expected: no output and exit code 0.

- [ ] **Step 5: Run existing support and save tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_support_upgrades tests.test_save_manager -v
```

Expected: all tests pass; batch integration has not changed support formulas or
the persisted level fields.

- [ ] **Step 6: Commit batch purchasing**

```powershell
git add main.py
git commit -m "feat: apply upgrade purchases as one batch"
```

### Task 4: Integrate Modal State and Mouse Controls

**Files:**
- Modify: `main.py:upgrade_UI`

- [ ] **Step 1: Add modal state and synchronization helpers inside `upgrade_UI()`**

After scrollbar drag state, add:

```python
    modal_row = None
    modal_selected_add = 0
    modal_max_add = 0
    modal_input_text = ""
    modal_input_active = False
    dragging_level_slider = False

    def sync_modal_value(value):
        nonlocal modal_selected_add, modal_input_text
        modal_selected_add = upgrade_selection.clamp_addition(value, modal_max_add)
        modal_input_text = str(modal_selected_add)

    def open_upgrade_modal(row):
        nonlocal modal_row, modal_max_add, modal_input_active
        modal_row = row
        modal_max_add = upgrade_selection.max_affordable_addition(
            row["cost_base"],
            row["level"],
            player.coin,
            row["level_offset"],
        )
        modal_input_active = True
        sync_modal_value(modal_max_add)

    def close_upgrade_modal():
        nonlocal modal_row, modal_input_active, dragging_level_slider
        modal_row = None
        modal_input_active = False
        dragging_level_slider = False
```

- [ ] **Step 2: Draw all store rows as clickable and render the modal last**

Change row presentation so affordability only controls its style, not whether
it can be clicked:

```python
            affordable = player.coin >= row["cost"]
            draw_button(
                screen,
                button,
                f'{row["label"]}  /  LV.{row["level"]}',
                hovered=button.collidepoint((mx, my)),
                style='primary' if affordable else 'secondary',
                disabled=False,
                subtitle=row["subtitle"],
            )
```

After drawing the back button, add:

```python
        modal_controls = None
        modal_total_cost = 0
        if modal_row is not None:
            modal_total_cost = upgrade_selection.total_upgrade_cost(
                modal_row["cost_base"],
                modal_row["level"],
                modal_selected_add,
                modal_row["level_offset"],
            )
            modal_controls = draw_upgrade_level_modal(
                screen,
                modal_row["label"],
                current_level=modal_row["level"],
                selected_add=modal_selected_add,
                max_add=modal_max_add,
                total_cost=modal_total_cost,
                input_text=modal_input_text,
                input_active=modal_input_active,
                mouse_pos=(mx, my),
            )
```

- [ ] **Step 3: Route modal mouse input before store input**

At the start of the event loop, after QUIT handling, add a modal branch that
ends with `continue`:

```python
            if modal_row is not None and modal_controls is not None:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if modal_controls["cancel"].collidepoint(event.pos):
                        close_upgrade_modal()
                    elif modal_controls["confirm"].collidepoint(event.pos):
                        if buy_upgrade_levels(modal_row["key"], modal_selected_add):
                            close_upgrade_modal()
                    elif modal_controls["minus"].collidepoint(event.pos):
                        sync_modal_value(modal_selected_add - 1)
                    elif modal_controls["plus"].collidepoint(event.pos):
                        sync_modal_value(modal_selected_add + 1)
                    elif (
                        modal_controls["slider"].inflate(0, 30).collidepoint(event.pos)
                        or modal_controls["slider_thumb"].collidepoint(event.pos)
                    ):
                        dragging_level_slider = True
                        sync_modal_value(
                            upgrade_selection.slider_value_from_x(
                                event.pos[0],
                                modal_controls["slider"].left,
                                modal_controls["slider"].width,
                                modal_max_add,
                            )
                        )
                    else:
                        modal_input_active = modal_controls["input"].collidepoint(event.pos)
                        if not modal_input_active:
                            sync_modal_value(modal_input_text)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging_level_slider = False
                elif event.type == pygame.MOUSEMOTION and dragging_level_slider:
                    sync_modal_value(
                        upgrade_selection.slider_value_from_x(
                            event.pos[0],
                            modal_controls["slider"].left,
                            modal_controls["slider"].width,
                            modal_max_add,
                        )
                    )
                continue
```

This `continue` is required so wheel scrolling, row clicks, scrollbar dragging,
and the back button cannot run while the modal is open.

- [ ] **Step 4: Change row clicks to open the modal**

Replace:

```python
buy_upgrade(row["key"])
```

with:

```python
open_upgrade_modal(row)
```

- [ ] **Step 5: Syntax-check and run focused tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile main.py ui.py upgrade_selection.py
.\.venv\Scripts\python.exe -m unittest tests.test_upgrade_selection tests.test_ui -v
```

Expected: compilation succeeds and focused tests pass.

- [ ] **Step 6: Commit mouse-driven modal integration**

```powershell
git add main.py
git commit -m "feat: open upgrade selector and handle mouse controls"
```

### Task 5: Add Numeric Keyboard Editing and Revalidation

**Files:**
- Modify: `main.py:upgrade_UI`

- [ ] **Step 1: Track selection and caret state**

Add with the other modal state:

```python
    modal_caret = 0
    modal_select_all = False
```

Update `sync_modal_value`:

```python
    def sync_modal_value(value):
        nonlocal modal_selected_add, modal_input_text, modal_caret, modal_select_all
        modal_selected_add = upgrade_selection.clamp_addition(value, modal_max_add)
        modal_input_text = str(modal_selected_add)
        modal_caret = len(modal_input_text)
        modal_select_all = False
```

In `open_upgrade_modal`, the existing `sync_modal_value(modal_max_add)` places
the caret at the end.

- [ ] **Step 2: Add key handling before modal mouse handling**

Inside the modal event branch, before mouse handling:

```python
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        close_upgrade_modal()
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        sync_modal_value(modal_input_text)
                        if buy_upgrade_levels(modal_row["key"], modal_selected_add):
                            close_upgrade_modal()
                    elif modal_input_active:
                        ctrl_down = bool(event.mod & pygame.KMOD_CTRL)
                        if ctrl_down and event.key == pygame.K_a:
                            modal_select_all = True
                            modal_caret = len(modal_input_text)
                        elif event.key == pygame.K_HOME:
                            modal_caret = 0
                            modal_select_all = False
                        elif event.key == pygame.K_END:
                            modal_caret = len(modal_input_text)
                            modal_select_all = False
                        elif event.key == pygame.K_LEFT:
                            modal_caret = max(0, modal_caret - 1)
                            modal_select_all = False
                        elif event.key == pygame.K_RIGHT:
                            modal_caret = min(len(modal_input_text), modal_caret + 1)
                            modal_select_all = False
                        elif event.key == pygame.K_BACKSPACE:
                            if modal_select_all:
                                modal_input_text = ""
                                modal_caret = 0
                            elif modal_caret > 0:
                                modal_input_text = (
                                    modal_input_text[:modal_caret - 1]
                                    + modal_input_text[modal_caret:]
                                )
                                modal_caret -= 1
                            modal_select_all = False
                            modal_selected_add = upgrade_selection.clamp_addition(
                                modal_input_text,
                                modal_max_add,
                            )
                        elif event.key == pygame.K_DELETE:
                            if modal_select_all:
                                modal_input_text = ""
                                modal_caret = 0
                            elif modal_caret < len(modal_input_text):
                                modal_input_text = (
                                    modal_input_text[:modal_caret]
                                    + modal_input_text[modal_caret + 1:]
                                )
                            modal_select_all = False
                            modal_selected_add = upgrade_selection.clamp_addition(
                                modal_input_text,
                                modal_max_add,
                            )
                        elif event.unicode.isdigit():
                            if modal_select_all:
                                modal_input_text = event.unicode
                                modal_caret = 1
                            else:
                                modal_input_text = (
                                    modal_input_text[:modal_caret]
                                    + event.unicode
                                    + modal_input_text[modal_caret:]
                                )
                                modal_caret += 1
                            modal_select_all = False
                            modal_selected_add = upgrade_selection.clamp_addition(
                                modal_input_text,
                                modal_max_add,
                            )
```

Keep the modal branch's final `continue`, so keys do not leak into other
UPGRADE controls.

- [ ] **Step 3: Revalidate affordability immediately before purchase**

Before calling `buy_upgrade_levels` from mouse or Enter confirmation, refresh:

```python
                        fresh_max = upgrade_selection.max_affordable_addition(
                            modal_row["cost_base"],
                            modal_row["level"],
                            player.coin,
                            modal_row["level_offset"],
                        )
                        if modal_selected_add > fresh_max:
                            modal_max_add = fresh_max
                            sync_modal_value(fresh_max)
                        elif buy_upgrade_levels(modal_row["key"], modal_selected_add):
                            close_upgrade_modal()
```

Use this same block for both confirmation paths. It protects the transaction
if live coin state changes while the modal is open.

- [ ] **Step 4: Syntax-check and run the full automated suite**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile main.py ui.py upgrade_selection.py
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: compilation succeeds and the full suite passes.

- [ ] **Step 5: Commit keyboard input and final integration**

```powershell
git add main.py
git commit -m "feat: support numeric upgrade level input"
```

### Task 6: Manual Game Verification

**Files:**
- No source changes expected

- [ ] **Step 1: Launch the game from the repository root**

Run:

```powershell
.\.venv\Scripts\python.exe main.py
```

- [ ] **Step 2: Verify the modal visual hierarchy**

Open `UPGRADE`, click `WEAPON DAMAGE`, and confirm:

- the existing UPGRADE page is dimmed but still visible;
- the modal uses the existing navy/cyan/gold tactical style;
- `CURRENT LEVEL` does not change while editing;
- `AFTER UPGRADE` equals current level plus the selected addition;
- total cost is shown in gold;
- the modal fits inside `600x900`.

- [ ] **Step 3: Verify all four selection methods**

For one upgrade:

- click minus and plus;
- click both ends and the middle of the slider;
- drag the circular thumb;
- press Ctrl+A and type a number;
- use Backspace, Delete, Left, Right, Home, and End;
- verify the input, thumb, projected level, and total cost stay synchronized.

- [ ] **Step 4: Verify transaction boundaries**

- Cancel and Escape leave coins and levels unchanged.
- Confirm deducts exactly the displayed total.
- Reopening shows the new current level.
- With an unaffordable paid upgrade, the modal opens at `+0` and Confirm is
  disabled.
- Store scrolling, row clicks, and Back do nothing while the modal is open.

- [ ] **Step 5: Verify all five upgrade types**

Confirm one batch for:

- Weapon Damage;
- Projectile Speed;
- Hull Capacity;
- Sentry Gun;
- Tactical Support.

Check that each stat/effect increases by the selected number of levels and the
Sentry Gun group refresh happens once.

- [ ] **Step 6: Verify save persistence**

Exit normally, relaunch, and confirm the purchased levels and remaining coins
are restored.

- [ ] **Step 7: Run final verification commands**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile main.py ui.py upgrade_selection.py
.\.venv\Scripts\python.exe -m pytest -q
git status --short
git log -6 --oneline
```

Expected:

- compilation succeeds;
- all tests pass;
- only intentional files are modified;
- the implementation commits appear in order.
