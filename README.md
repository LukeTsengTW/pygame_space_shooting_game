# Pygame Space Shooting Game

A feature-rich 2D vertical-scrolling space shooter built with Python and Pygame, featuring 15 campaign levels, an unlockable hard mode, boss battles, persistent upgrades, configurable controls, automated tests, and standalone Windows builds.

## Highlights

- 2D vertical-scrolling space shooter built with Pygame.
- 15-level campaign with an unlockable hard campaign.
- Boss battles, level-based enemy progression, and animated combat effects.
- Coin-funded upgrades for player combat, survivability, sentry guns, and tactical support.
- Persistent progression, upgrades, and settings.
- Keyboard or mouse flight control, configurable from Settings.
- Automated tests for progression, difficulty scaling, UI helpers, persistence, backgrounds, support systems, and asset validation.
- Standalone Windows builds through PyInstaller.

## Demo

[![Gameplay demonstration](https://img.youtube.com/vi/mKqw35v4tzM/0.jpg)](https://www.youtube.com/watch?v=mKqw35v4tzM)

Click the preview image above to watch the gameplay demonstration.

## Requirements

- Python 3.12
- Pygame 2.6.1
- The instructions below are written for Windows PowerShell. The standalone executable build process currently targets Windows.

## Installation

Python 3.12 is recommended. If needed, install it with:

```powershell
winget install -e --id Python.Python.3.12
```

Restart PowerShell, open the repository root, and create the project environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pygame==2.6.1
```

Verify the installed Pygame version:

```powershell
python -c "import pygame; print(pygame.version.ver)"
```

If PowerShell blocks activation, allow it for the current process and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run the Game

Run the game from the repository root so its relative paths to images, music, and sound effects resolve correctly:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Controls

- **Keyboard mode (default):** move with the arrow keys.
- **Mouse mode:** move the ship by moving the mouse.
- **Configuration:** switch between keyboard and mouse control in **Settings**. Settings also include a music-volume control.

## Features

### Campaign and Difficulty

The normal campaign contains 15 selectable levels that unlock as progress is made. Completing the normal campaign unlocks a separate hard campaign, whose difficulty scaling increases enemy health and damage, spawn frequency, and boss attack cadence.

### Enemies and Boss Battles

Enemy types, spawn conditions, health, and damage progress with the campaign. Boss encounters are integrated into the level flow, with dedicated boss health-bar presentation and distinct attack behavior.

### Progression and Upgrades

Defeated enemies award coins that can be spent in the upgrade store. Available upgrades include damage, bullet speed, maximum lives, sentry guns, and tactical support. The game persists campaign progress, upgrade levels, coins, control mode, volume, and opening-sequence state.

### Combat and Items

Combat includes player bullets, enemy projectiles, explosions, hit effects, and enemy rewards. Health-restoration and temporary-shield pickups provide recovery options during play.

### Interface and Visual Effects

The game includes an opening sequence with skip handling, menu and level-selection interfaces, an upgrade-purchase flow, a gameplay HUD, boss health bars, scrolling backgrounds, and animated combat feedback.

### Tooling and Distribution

The `tools/` directory contains utilities for preparing vertical background tiles and validating level backgrounds. PyInstaller configuration supports a bundled Windows distribution.

## Testing

Run the automated suite from the repository root with either test runner:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

The suite covers level progression, hard-mode scaling, boss health display, scrolling backgrounds, opening-sequence skipping, HUD safe zones, UI and upgrade calculations, support systems, save-data handling, and asset-validation helpers.

## Build a Windows Executable

Install the packaging tools into the project environment:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller pillow
```

Build the Windows application with the bundled spec file:

```powershell
.\.venv\Scripts\pyinstaller.exe space_shooter.spec --noconfirm
```

The build is written to `dist\SpaceShooter\`. Run `dist\SpaceShooter\SpaceShooter.exe`, and distribute the entire `dist\SpaceShooter` folder so the `_internal` directory remains beside the executable.

The configuration produces a windowed `onedir` build. `space_shooter.spec` packages `img/`, `music/`, `sound_effect/`, `font.ttf`, and `icon.png`; `pyinstaller_runtime_hook.py` changes the working directory to the bundled resources so the game's relative asset paths continue to work.

## Project Structure

```text
main.py                       Game entry point, menus, and gameplay loop
config.py                     Runtime configuration, shared tuning, and audio setup
enemy.py / player.py          Enemy and player implementations
background.py / ui.py         Scrolling-background and interface helpers
level_progress.py             Level-unlock rules
hard_mode.py                  Difficulty-scaling helpers
save_manager.py               Persistent save-data handling
tests/                        Automated tests for isolated logic and UI behavior
tools/                        Background preparation and validation utilities
docs/                         Design specifications and implementation plans
img/                          Image assets
music/                        Music assets
sound_effect/                 Sound-effect assets
space_shooter.spec            PyInstaller build configuration
```

## Architecture and Maintainability

The main runtime flow remains centered in `main.py`, while gameplay entities, configuration, persistence, backgrounds, UI helpers, progression rules, difficulty scaling, and other testable logic are maintained in dedicated modules. Several logic-heavy components—such as save management, boss health display, opening-sequence skipping, and upgrade calculations—are isolated from the runtime loop so they can be tested independently.

Build packaging is maintained through the PyInstaller spec and runtime hook, while asset-processing and validation utilities remain separate in `tools/`.

## Troubleshooting

### Pygame installation fails with Python 3.14

Installing `pygame==2.6.1` on Windows with Python 3.14 can fail with messages such as:

```text
ModuleNotFoundError: No module named 'distutils.msvccompiler'
ModuleNotFoundError: No module named 'setuptools._distutils.msvccompiler'
ERROR: Failed to build 'pygame' when getting requirements to build wheel
```

Pygame 2.6.1 does not provide a compatible Windows wheel for this Python version, causing pip to attempt a local source build. Create and use the Python 3.12 virtual environment described above instead of adding SDL or Visual C++ build dependencies.

In VS Code, select the project interpreter through **Python: Select Interpreter** and choose:

```text
.\.venv\Scripts\python.exe
```

## Asset Credits

### Backgrounds

- ChatGPT Image Generation

### CC0 Visual Assets

- Space Main Ship: https://foozlecc.itch.io/void-main-ship
- Enemy 1 Series: https://foozlecc.itch.io/void-fleet-pack-1
- Enemy 2 Series: https://foozlecc.itch.io/void-fleet-pack-2
- Enemy 3 Series: https://foozlecc.itch.io/void-fleet-pack-3
- Items: https://foozlecc.itch.io/void-pickups-pack

These visual assets are identified as [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

### Background Music

The following music tracks were created by **Oblidivm** and are available from the
[Space Shooter Music](https://opengameart.org/content/space-shooter-music)
asset collection under the
[CC BY 3.0 License](https://creativecommons.org/licenses/by/3.0/).

No modifications, editing, trimming, or format conversion were made to these files.

- `Battle in the Stars.ogg`
- `Brave Pilots (Menu Screen).ogg`
- `DeathMatch (Boss Theme).ogg`
- `Defeated (Game Over Tune).ogg`
- `SkyFire (Title Screen).ogg`
- `Victory Tune.ogg`

### Sound Effects

The following sound effects are used under the
[Pixabay Content License](https://pixabay.com/service/license-summary/):

- [Laser Sound Effect](https://pixabay.com/sound-effects/film-special-effects-laser-312360/)
- [Boom Sound Effect](https://pixabay.com/sound-effects/film-special-effects-boom-128320/)

Laser Sound Effect was created by [Ahmed_Abdulaal](https://pixabay.com/users/ahmed_abdulaal-49290858/), and Boom Sound Effect was created by [SoundReality](https://pixabay.com/users/soundreality-31074404/).

## Project History

This project began as a high-school game-development project and has continued to evolve through feature development, automated testing, packaging improvements, and ongoing code maintenance.

## Contributing

Bug reports, feature proposals, and pull requests are welcome. Please open a GitHub Issue with clear reproduction steps for bugs or a concrete use case for proposed features.

Keep pull requests focused, include relevant tests where practical, and verify that newly added assets have compatible licenses and clear source information.

## License

The [MIT License](LICENSE) applies only to the source code in this repository. Background music, visual assets, and sound effects remain subject to their respective licenses listed in [Asset Credits](#asset-credits).
