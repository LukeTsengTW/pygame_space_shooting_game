# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

A 2D top-down vertical-scrolling space shooter built with Pygame (Python 3.12, Pygame 2.6.1). Single-player, 15 normal levels + an unlockable hard campaign, an in-menu upgrade store, and a boss every 5th level.

## Exploring code: use the code-review-graph MCP tools first

This project has a knowledge graph. **Prefer the `code-review-graph` MCP tools over Grep/Glob/Read for exploration** — they are faster, cheaper (fewer tokens), and return structural context (callers, dependents, test coverage) that file scanning can't.

| Goal | Tool |
| ---- | ---- |
| Find a function/class by name or keyword | `semantic_search_nodes` |
| Trace callers / callees / imports / tests | `query_graph` (`callers_of`, `callees_of`, `imports_of`, `tests_for`) |
| Review code changes (risk-scored) | `detect_changes`, then `get_review_context` for snippets |
| Understand blast radius of a change | `get_impact_radius` |
| Find impacted execution paths | `get_affected_flows` |
| High-level structure | `get_architecture_overview`, `list_communities` |
| Plan renames / find dead code | `refactor_tool` |

The graph auto-updates on file changes via hooks. Fall back to Grep/Glob/Read only when the graph doesn't cover what you need.

> Note: the graph may be empty until built (`build_or_update_graph_tool`), and on Windows the embedding / `semantic_search` tools can hang against the local model — if so, run the Python API in a subprocess instead and lean on `query_graph` / `detect_changes`.

## Commands

All commands assume the project virtualenv at `.venv` and **must run from the project root** (asset paths are relative to the working directory).

```powershell
# Run the game
.\.venv\Scripts\python.exe main.py

# Run all tests (pytest and unittest both work)
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m unittest discover -s tests

# Run a single test module / case
.\.venv\Scripts\python.exe -m unittest tests.test_level_progress
.\.venv\Scripts\python.exe -m unittest tests.test_level_progress.LevelProgressTests.test_clearing_the_latest_level_unlocks_the_next_level

# Syntax-check the entry point without launching pygame
.\.venv\Scripts\python.exe -m py_compile main.py

# Build the standalone Windows .exe -> dist\SpaceShooter\
.\.venv\Scripts\pyinstaller.exe space_shooter.spec --noconfirm
```

Type checking uses pyright; `pyrightconfig.json` points it at `.venv`.

## Architecture

### `main.py` runs on import — it is the whole game

`main.py` is not a library of functions; module-level code at the top initializes pygame and loads every background, and the `while running:` game loop sits at the bottom of the file. **Importing `main.py` launches the game.** This is why no test imports it — tests only cover modules that are safe to import in isolation.

The game flow is a stack of blocking sub-loops: `display_opening_screen()` → `main_menu()` → screen functions (`chose_level`, `upgrade_UI`, `setting`, `credits`, `pause_menu`, `stage_clear_screen`, `game_over_screen`, etc.). Each runs its own `while ... clock.tick(60)` loop and calls back into others, so the call stack nests rather than returning to a central dispatcher. The bottom `while running` loop (`clock.tick(180)`) is the actual gameplay loop; menu screens are reached by calling into it.

### Global mutable state via wildcard imports

Most modules do `from config import *`, and sprite collections live in `shared.py` as module-level pygame `Group`s (`all_sprites`, `enemies`, `bullets`, `enemy_bullets`). Tuning values (`BULLET_SPEED`, `max_lives`, `PLAYER_SPEED`, `player_bullet_angle`) are module globals in `config.py` mutated in place by the upgrade store. There is no central game-state object — state is the union of these module globals plus `main.py`'s own globals (`level`, `score`, `highest_unlocked_level`, etc.).

### `config.py` has import-time side effects

Importing `config` calls `pygame.mixer.init()` and loads sound files from `sound_effect/`. So any module that imports config (directly or via `import *`) requires the audio assets present and the cwd set to the project root. This is another reason `player.py`/`enemy.py` aren't unit-tested directly.

### Enemy / level system: parallel structures keyed by `'enemies_N'`

Enemies are identified by string keys `enemies_1` .. `enemies_18` (18 base/support types; `enemies_5`, `enemies_11`, `enemies_18` are the three bosses). The same key set is repeated across several parallel data structures that **must stay in sync** when adding or tuning an enemy:

- `config.py`: `enemy_hp`, `ENEMY_GENERATION_THRESHOLDS` (spawn probabilities), `BOSS_GENERATION_ONCE` (per-boss spawned-flag latches).
- `main.py`: `enemies_p` (one sprite `Group` per key), `enemy_damage_values`, the `check_bullet_hit(...)` call per key (sets score increment, drop rates, explosion class, coin reward), and the `generate_enemy(...)` calls inside the gameplay loop gated by `level`.

`enemy.py` defines an `Enemy` base class; concrete `Enemy_1`..`Enemy_15` and `Boss_1`..`Boss_3` subclasses hardcode their sprite/shield asset paths, speed, hp (from `enemy_hp`), and per-frame bullet behavior. "Support" enemies (`Is_support=True`, e.g. `Enemy_4`) shield a target enemy and track it via a class-level `targets` list. Enemy art swaps every 5 levels (`lv1_to_5/`, `lv6_to_10/`, etc.).

Level progression is score-gated: advance when `score > 100 + (level * 10) * 9`. Bosses spawn once per level via the `BOSS_GENERATION_ONCE` latches, which `reset_enemies()` / `reset_continue_game()` clear.

### Pure / testable modules

These have no import-time pygame side effects (or guard them) and hold the unit-tested logic:

- `level_progress.py` — `can_select_level`, `unlocked_level_after_clear` (level unlock rules).
- `background.py` — `ScrollingBackground` (offset/wrap math; tests inject fake surfaces, no real pygame needed).
- `opening_skip.py` — opening-cutscene skip state machine.
- `boss_health.py` — `BossHealthDisplayState` (delayed/animated boss health-bar ratio).
- `ui.py` — pure drawing helpers (`draw_button`, `draw_panel`, `draw_gameplay_hud`, `draw_boss_health_bar`, `level_grid_rects`, `COLORS`, ...). UI tests need a surface, so they set `SDL_VIDEODRIVER=dummy` before importing pygame and call `pygame.display.set_mode((1,1))`.

When adding logic that needs testing, prefer extracting it into a pure module like these rather than embedding it in `main.py`.

### Layout constants

Screen is `600x900`. The top `HUD_HEIGHT + BOSS_BAR_HEIGHT` pixels (`GAMEPLAY_TOP`) is reserved HUD/boss-bar safe zone; the player and enemies are clamped below it.

## Conventions & gotchas

- **Run from project root.** All asset references (`img/`, `music/`, `sound_effect/`, `font.ttf`, `icon.png`) are relative paths. In the packaged build, `pyinstaller_runtime_hook.py` `chdir`s into the bundle so these keep working — keep new assets relative and add them to the `datas` list in `space_shooter.spec`.
- `tests/` and `tools/` are packages (`__init__.py`); tests import project modules by top-level name, so run them from the repo root.
- `tools/` holds asset-pipeline scripts (`make_vertical_tile.py`, `validate_level_backgrounds.py`) — used to prepare/validate level backgrounds, not part of the runtime.
- `docs/superpowers/specs/` and `docs/superpowers/plans/` contain design specs and implementation plans from the superpowers workflow; consult them for the intent behind recent features (backgrounds, tactical UI, boss health bar, HUD safe zone, opening skip).
- `build/` and `dist/` are PyInstaller output and gitignored.
