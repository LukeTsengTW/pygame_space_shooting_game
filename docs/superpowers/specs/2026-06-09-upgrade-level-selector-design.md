# Upgrade Level Selector Design

**Date:** 2026-06-09
**Status:** Approved visual direction

## Goal

Replace the UPGRADE screen's immediate one-level purchase with a modal that
lets the player choose how many levels to add in one transaction.

The approved modal follows the existing tactical UI:

- dark navy cut-corner panels;
- cyan borders, controls, and slider glow;
- muted blue-gray labels;
- gold cost and projected-level accents;
- the existing `font.ttf` and uppercase English labels.

The modal always shows the current level as read-only. Its editable value is
the number of levels to add, not an absolute target level. Opening the modal
defaults that value to the highest number of levels the player can currently
afford.

## Selected Approach

Use a modal state inside `upgrade_UI()` with pure calculation helpers in a new
module.

Alternatives considered:

1. Repeatedly call the existing one-level purchase function. This is simple,
   but performs multiple saves and gameplay side effects during one confirmed
   transaction.
2. Store an absolute target level. This maps directly to the slider, but it
   conflicts with the approved requirement that the editable value means
   "levels to add."
3. **Selected:** calculate and apply one batch transaction. This keeps the
   current level immutable in the modal, deducts coins once, applies side
   effects once, and saves once.

## Modal Layout

Clicking any upgrade row opens a centered modal over a dimmed UPGRADE screen.
The store list and scrollbar remain visible but cannot receive input while the
modal is open.

Top to bottom:

1. Upgrade name and cyan divider.
2. `CURRENT LEVEL` read-only stat card.
3. `AFTER UPGRADE` read-only projected level card.
4. `LEVELS TO ADD` numeric text input.
5. Minus button, horizontal slider, and plus button.
6. Slider endpoint labels: `+0` and `MAX +N`.
7. `TOTAL UPGRADE COST` in gold.
8. `CANCEL` and `CONFIRM` buttons.

The input displays the selected addition with a leading plus sign when it is
not being edited, for example `+9`. The stored/editable content remains digits
only so keyboard editing is predictable.

## Interaction

### Opening

- Every upgrade row is clickable, even if no paid level is affordable.
- Compute `max_add` from the current level, current coins, and that upgrade's
  price formula.
- Initialize `selected_add = max_add`.
- Focus the numeric input immediately.
- If `max_add == 0`, the slider remains at zero and `CONFIRM` is disabled.

The existing basic upgrades have a zero-cost first level at level zero. This
existing behavior is preserved, so a new save with zero coins can select one
free level for those upgrades.

### Minus and plus

- Minus changes `selected_add` by `-1`.
- Plus changes `selected_add` by `+1`.
- The value is clamped to `0..max_add`.
- A button at its limit is visually disabled.
- These controls never lower an already purchased level.

### Slider

- The full track maps to integer additions from `0` to `max_add`.
- Clicking the track jumps to the nearest integer value.
- Dragging the circular thumb updates the value continuously, rounded to the
  nearest integer.
- The thumb, input, projected level, and total cost update together.
- When `max_add == 0`, the thumb stays at the start and dragging is disabled.

### Numeric input

- Accept digits, Backspace, Delete, Left/Right, Home/End, and Ctrl+A.
- Ignore non-numeric typed characters.
- Empty text is allowed temporarily while editing and previews as zero.
- On focus loss or confirmation, parse and clamp to `0..max_add`.
- Values above the affordable maximum become `max_add`; negative values are
  not accepted.
- Enter confirms when the clamped value is greater than zero.
- Escape cancels and closes the modal without changing coins or levels.

### Confirmation

`CONFIRM` is enabled only when:

- `selected_add > 0`; and
- the recomputed total cost is no greater than the player's current coins.

On confirmation:

1. Recompute the total cost from live level and coin values.
2. Reject the transaction and refresh the modal maximum if it is no longer
   affordable.
3. Deduct the total once.
4. Increase the selected upgrade level by `selected_add`.
5. Apply the matching gameplay effect by the same amount.
6. Run upgrade-specific side effects once.
7. Auto-save once.
8. Close the modal and redraw the updated UPGRADE row.

`CANCEL`, Escape, and closing the modal never mutate game state.

## Cost Calculation

Batch cost must equal buying the same levels one at a time under the current
game formulas.

For a current level `L` and addition count `N`:

| Upgrade | Cost to buy from level `k` to `k + 1` |
| --- | --- |
| Weapon damage | `1234 * k` |
| Projectile speed | `321 * k` |
| Hull capacity | `5432 * k` |
| Sentry gun | `50000 * (k + 1)` |
| Tactical support | `70000 * (k + 1)` |

The total is the sum for `k = L` through `L + N - 1`.

Examples:

- Damage level `0`, add `2`: `0 + 1234 = 1234`.
- Sentry level `0`, add `2`: `50000 + 100000 = 150000`.

`max_add` is the largest non-negative `N` whose total does not exceed the
available coins.

## Components

### New pure module: `upgrade_selection.py`

No pygame imports.

```text
level_purchase_cost(base_cost, level, level_offset=0) -> int
total_upgrade_cost(base_cost, current_level, add_levels, level_offset=0) -> int
max_affordable_addition(base_cost, current_level, coins, level_offset=0) -> int
clamp_addition(value, max_add) -> int
slider_value_from_x(mouse_x, track_left, track_width, max_add) -> int
slider_x_from_value(value, track_left, track_width, max_add) -> int
```

The three basic upgrades use `level_offset=0`; sentry and tactical support use
`level_offset=1`.

### `ui.py`

Add drawing/layout helpers only:

- modal rectangle and control rectangle calculation;
- dimmed modal backdrop;
- current/projected level cards;
- numeric input;
- horizontal integer slider with circular thumb;
- disabled/enabled minus, plus, cancel, and confirm buttons.

These helpers return their interactive rectangles so `main.py` can route
events without duplicating layout coordinates.

### `main.py`

- Extend each upgrade row with its cost base and level offset.
- Replace row-click `buy_upgrade(row["key"])` with modal state creation.
- Route modal mouse and keyboard events before store scrolling or row events.
- Replace the one-level purchase path with a batch purchase function that
  revalidates cost and applies the confirmed addition atomically.
- Keep sentry spawning to one refresh after a confirmed sentry purchase.
- Keep one `autosave()` per successful confirmation.

## Data Flow

```text
row click
  -> read current level + coin
  -> calculate max affordable addition
  -> open modal at selected_add = max_add

minus / plus / text / slider
  -> clamp selected_add
  -> calculate projected level + total cost
  -> redraw modal

confirm
  -> recompute against live state
  -> deduct total
  -> apply N levels and effects
  -> run one side effect + one autosave
  -> close modal
```

## Testing

### Pure unit tests

Add `tests/test_upgrade_selection.py`:

- basic-upgrade cost preserves the free level-zero purchase;
- support-upgrade cost starts at its base price;
- total cost equals the sum of sequential one-level costs;
- affordable maximum returns the highest payable addition;
- zero coins still allow the existing free first basic level;
- zero coins allow no sentry/tactical level;
- clamping handles negative, oversized, and invalid values;
- slider coordinate/value conversion handles both endpoints, midpoint
  rounding, and `max_add == 0`.

### Existing tests

- Add UI geometry tests for all modal controls being inside the `600x900`
  screen and not overlapping incorrectly.
- Run the full test suite.
- Run `py_compile` on `main.py`, `ui.py`, and `upgrade_selection.py`.

### Manual verification

For each of the five upgrade rows:

- modal opens instead of immediately buying one level;
- current level remains fixed;
- default addition is the maximum affordable amount;
- minus, plus, slider, and numeric input stay synchronized;
- total cost matches sequential pricing;
- cancel leaves state unchanged;
- confirm deducts the displayed amount and applies all selected levels;
- scrolling and background row clicks are blocked while modal is open;
- reopening reflects the newly saved level and coin balance.

## Out of Scope

- Selling upgrades or refunding coins.
- Lowering an already purchased level.
- Changing existing upgrade price formulas or balance.
- Adding a permanent maximum level.
- Redesigning the UPGRADE list or its vertical scrollbar.
