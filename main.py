import atexit
import sys
import random
from itertools import chain

import save_manager
import support_upgrades
import upgrade_selection
import config
import hard_mode
from background import ScrollingBackground
from boss_health import BossHealthDisplayState
from config import *
from enemy import Enemy, Enemy_1, Enemy_2, Enemy_3, Enemy_4, Enemy_5, Enemy_6, Enemy_7, Enemy_8, Enemy_9, Enemy_10, Enemy_11, Enemy_12, Enemy_13, Enemy_14, Enemy_15, Boss_1, Boss_2, Boss_3
from item import Item_1, Item_2
from explosion import HitSpark, Explosion_1, Explosion_2, Explosion_3, Explosion_4, Explosion_5, Explosion_6, Explosion_7, Explosion_8, Explosion_9, Explosion_10, Explosion_11, Explosion_12, Explosion_13, Explosion_14, Explosion_15, Explosion_16, Explosion_17, Explosion_18
from level_progress import can_select_level, unlocked_level_after_clear
from opening_skip import (
    OPENING_SKIP_PROMPT,
    OpeningSkipState,
    is_opening_skip_input,
)
from player import Player
from sentry import SentryGun
from shared import enemy_bullets, enemies, all_sprites, bullets
from ui import (
    COLORS,
    create_creator_card,
    draw_boss_health_bar,
    draw_button,
    draw_gameplay_hud,
    draw_heading,
    draw_modal_backdrop,
    draw_opening_briefing,
    draw_opening_skip_prompt as draw_ui_opening_skip_prompt,
    draw_panel,
    draw_slider,
    draw_stat_card,
    draw_tactical_starfield,
    draw_text as draw_ui_text,
    draw_upgrade_level_modal,
    level_grid_rects,
)

items = {
    'item_1': pygame.sprite.Group(),
    'item_2': pygame.sprite.Group(),
}
enemies_p = {f"enemies_{i}": pygame.sprite.Group() for i in range(1, 19)}
BOSS_GROUP_KEYS = ('enemies_5', 'enemies_11', 'enemies_18')

level_start_time = 0

damage_level = 0
damage_level_need_coin = 0
bullet_speed_level = 0
bullet_speed_level_need_coin = 0
live_level = 0
live_level_need_coin = 0
sentry_gun_level = 0
tactical_support_level = 0
tactical_support_last_trigger_time = -999_999_999
tactical_support_effect_until = 0
tactical_support_banner_until = 0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_icon(pygame.image.load('icon.png'))
pygame.display.set_caption('Space Shooter - Pygame Edition v1.1.0 - By: @LukeTseng')
font = pygame.font.Font('font.ttf', 36)
clock = pygame.time.Clock()

hard_level = 1
level = 1
highest_unlocked_level = level

is_complete_game = False

opening_seen = False

backgrounds = [pygame.image.load(f'img/background/lv{i}_background.jpg') for i in range(1, 21)]
gameplay_background = ScrollingBackground(backgrounds[0], speed=1)

score = 0 
running = True 

player = Player()
all_sprites.add(player)
sentry_guns = pygame.sprite.Group()
boss_health_display = BossHealthDisplayState()

ENEMY_REWARD_CONFIG = (
    ('enemies_1', 2, Explosion_1, 10),
    ('enemies_2', 3, Explosion_2, 20),
    ('enemies_3', 4, Explosion_3, 30),
    ('enemies_4', 5, Explosion_4, 40),
    ('enemies_5', 200, Explosion_5, 10000),
    ('enemies_6', 6, Explosion_6, 50),
    ('enemies_7', 7, Explosion_7, 60),
    ('enemies_8', 8, Explosion_8, 70),
    ('enemies_9', 9, Explosion_9, 80),
    ('enemies_10', 10, Explosion_10, 90),
    ('enemies_11', 600, Explosion_11, 50000),
    ('enemies_12', 11, Explosion_12, 100),
    ('enemies_13', 12, Explosion_13, 110),
    ('enemies_14', 13, Explosion_14, 120),
    ('enemies_15', 14, Explosion_15, 130),
    ('enemies_16', 15, Explosion_16, 140),
    ('enemies_17', 16, Explosion_17, 150),
    ('enemies_18', 1000, Explosion_18, 100000),
)
TACTICAL_SUPPORT_TARGET_KEYS = support_upgrades.tactical_support_target_keys(
    tuple(row[0] for row in ENEMY_REWARD_CONFIG),
    BOSS_GROUP_KEYS,
)
TACTICAL_SUPPORT_REWARD_CONFIG = tuple(
    row for row in ENEMY_REWARD_CONFIG if row[0] in TACTICAL_SUPPORT_TARGET_KEYS
)

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)


def gather_save_state():
    return {
        "version": 1,
        "progression": {
            "highest_unlocked_level": highest_unlocked_level,
            "is_complete_game": is_complete_game,
            "hard_level": hard_level,
        },
        "economy": {
            "coin": player.coin,
            "damage_level": damage_level,
            "bullet_speed_level": bullet_speed_level,
            "live_level": live_level,
            "sentry_gun_level": sentry_gun_level,
            "tactical_support_level": tactical_support_level,
        },
        "settings": {
            "volume_level": volume_level,
            "control_mode": player.control,
            "opening_seen": opening_seen,
        },
    }


def apply_save_state(data):
    global highest_unlocked_level, hard_level, is_complete_game
    global damage_level, bullet_speed_level, live_level, sentry_gun_level, tactical_support_level
    global damage_level_need_coin, bullet_speed_level_need_coin, live_level_need_coin
    global max_lives, BULLET_SPEED, volume_level, opening_seen

    progression = data["progression"]
    economy = data["economy"]
    settings = data["settings"]

    highest_unlocked_level = progression["highest_unlocked_level"]
    is_complete_game = progression["is_complete_game"]
    hard_level = progression["hard_level"]

    damage_level = economy["damage_level"]
    bullet_speed_level = economy["bullet_speed_level"]
    live_level = economy["live_level"]
    sentry_gun_level = economy["sentry_gun_level"]
    tactical_support_level = economy["tactical_support_level"]

    damage_level_need_coin = damage_level * 1234
    bullet_speed_level_need_coin = bullet_speed_level * 321
    live_level_need_coin = live_level * 5432

    max_lives = 10 + live_level
    BULLET_SPEED = 20 + bullet_speed_level

    player.coin = economy["coin"]
    player.damage = 50 + damage_level
    player.lives = max_lives
    player.control = settings["control_mode"]

    volume_level = settings["volume_level"]
    pygame.mixer.music.set_volume(volume_level)

    opening_seen = settings["opening_seen"]


def autosave():
    save_manager.save_state(gather_save_state())


def reset_game():
    global score, level, level_start_time

    for sprite in all_sprites:
        sprite.kill()

    all_sprites.add(player)
    player.lives = max_lives
    spawn_sentry_guns()
    reset_tactical_support_cooldown()
    score, level = 0, 1
    level_start_time = pygame.time.get_ticks()

def reset_continue_game():
    global score, level_start_time

    for sprite in all_sprites:
        sprite.kill()

    all_sprites.add(player)
    player.lives = max_lives
    spawn_sentry_guns()
    reset_tactical_support_cooldown()
    score = 0
    level_start_time = pygame.time.get_ticks()

    BOSS_GENERATION_ONCE['enemies_5'] = False
    BOSS_GENERATION_ONCE['enemies_11'] = False
    BOSS_GENERATION_ONCE['enemies_18'] = False


def spawn_sentry_guns():
    for sentry in sentry_guns:
        sentry.kill()

    stats = support_upgrades.sentry_gun_stats(sentry_gun_level)
    if not stats["active"]:
        return

    for index in range(stats["count"]):
        sentry = SentryGun(
            index,
            stats["count"],
            stats["lives"],
            stats["damage"],
            stats["bullet_speed"],
            stats["shot_interval_ms"],
        )
        sentry_guns.add(sentry)
        all_sprites.add(sentry)


def reset_tactical_support_cooldown():
    global tactical_support_last_trigger_time, tactical_support_effect_until, tactical_support_banner_until
    stats = support_upgrades.tactical_support_stats(tactical_support_level)
    now = pygame.time.get_ticks()
    tactical_support_last_trigger_time = support_upgrades.reset_tactical_support_cooldown(
        now,
        stats["cooldown_ms"],
    )
    tactical_support_effect_until = 0
    tactical_support_banner_until = 0

current_text = 0 
def setting():
    global current_text, volume_level
    setting_running = True
    text_options = ['Control the sprite with keyboard', 'Control the sprite with cursor']

    control_button = pygame.Rect(90, 270, 420, 82)
    slider_rect = pygame.Rect(120, 490, 360, 18)
    back_button = pygame.Rect(180, 700, 240, 58)

    setting_background = ScrollingBackground(
        pygame.image.load('img/background/setting_background.jpg'),
        speed=2,
    )

    while setting_running:
        setting_background.advance()
        setting_background.draw(screen)

        mx, my = pygame.mouse.get_pos()
        draw_panel(screen, pygame.Rect(50, 145, 500, 655), alpha=232)
        draw_heading(screen, 'Settings', 'FLIGHT CONTROL CONFIGURATION', y=82)

        draw_ui_text(screen, 'CONTROL MODE', 16, COLORS['muted'], (90, 235), anchor='midleft')
        text = text_options[current_text]
        draw_button(
            screen,
            control_button,
            text,
            hovered=control_button.collidepoint((mx, my)),
            style='primary',
            subtitle='CLICK TO SWITCH INPUT SYSTEM',
        )

        draw_ui_text(screen, 'MASTER VOLUME', 16, COLORS['muted'], (90, 445), anchor='midleft')
        draw_slider(screen, slider_rect, volume_level)
        volume_percentage = f"{int(volume_level * 101)}%"
        draw_ui_text(screen, volume_percentage, 24, COLORS['text'], (SCREEN_WIDTH // 2, 545))
        draw_button(
            screen,
            back_button,
            'BACK TO MENU',
            hovered=back_button.collidepoint((mx, my)),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and event.buttons[0] == 1):
                if slider_rect.collidepoint((mx, my)):
                    volume_level = max(0.0, min(1.0, (mx - slider_rect.x) / slider_rect.width))
                    pygame.mixer.music.set_volume(volume_level)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if control_button.collidepoint((mx, my)):
                        current_text = (current_text + 1) % len(text_options)
                        if current_text == 0:
                            player.control = 0
                        else:
                            player.control = 1
                    if back_button.collidepoint((mx, my)):
                        setting_running = False

        pygame.display.update()
        clock.tick(60)


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def get_upgrade_rows():
    sentry_cost = support_upgrades.next_upgrade_cost(
        support_upgrades.SENTRY_GUN_BASE_COST,
        sentry_gun_level,
    )
    tactical_cost = support_upgrades.next_upgrade_cost(
        support_upgrades.TACTICAL_SUPPORT_BASE_COST,
        tactical_support_level,
    )
    sentry_stats = support_upgrades.sentry_gun_stats(max(1, sentry_gun_level))
    tactical_stats = support_upgrades.tactical_support_stats(max(1, tactical_support_level))
    return (
        {
            "key": "damage",
            "label": "WEAPON DAMAGE",
            "level": damage_level,
            "cost": damage_level_need_coin,
            "cost_base": 1234,
            "level_offset": 0,
            "subtitle": f"COST {damage_level_need_coin:,} COINS\nCURRENT DMG {player.damage}  /  +1 DAMAGE",
        },
        {
            "key": "bullet_speed",
            "label": "PROJECTILE SPEED",
            "level": bullet_speed_level,
            "cost": bullet_speed_level_need_coin,
            "cost_base": 321,
            "level_offset": 0,
            "subtitle": f"COST {bullet_speed_level_need_coin:,} COINS\nCURRENT SPD {BULLET_SPEED}  /  +1 SPEED",
        },
        {
            "key": "lives",
            "label": "HULL CAPACITY",
            "level": live_level,
            "cost": live_level_need_coin,
            "cost_base": 5432,
            "level_offset": 0,
            "subtitle": f"COST {live_level_need_coin:,} COINS  /  +1 LIFE",
        },
        {
            "key": "sentry",
            "label": "SENTRY GUN",
            "level": sentry_gun_level,
            "cost": sentry_cost,
            "cost_base": support_upgrades.SENTRY_GUN_BASE_COST,
            "level_offset": 1,
            "subtitle": (
                f"COST {sentry_cost:,} COINS\n"
                f"{sentry_stats['count']} UNIT  {sentry_stats['lives']} LIVES  "
                f"{sentry_stats['damage']} DMG  SPD {sentry_stats['bullet_speed']}  "
                f"INT {sentry_stats['shot_interval_ms']}MS"
            ),
        },
        {
            "key": "tactical",
            "label": "TACTICAL SUPPORT",
            "level": tactical_support_level,
            "cost": tactical_cost,
            "cost_base": support_upgrades.TACTICAL_SUPPORT_BASE_COST,
            "level_offset": 1,
            "subtitle": (
                f"COST {tactical_cost:,} COINS  /  "
                f"HP <= {round(tactical_stats['trigger_ratio'] * 100)}%  CD {tactical_stats['cooldown_ms'] // 1000}s"
            ),
        },
    )


def draw_vertical_scrollbar(surface, track_rect, scroll_offset, max_scroll):
    if max_scroll <= 0:
        return None

    track_rect = pygame.Rect(track_rect)
    pygame.draw.rect(surface, COLORS["track"], track_rect, border_radius=track_rect.width // 2)
    thumb_height = max(46, round(track_rect.height * track_rect.height / (track_rect.height + max_scroll)))
    travel = track_rect.height - thumb_height
    thumb_y = track_rect.y + round((scroll_offset / max_scroll) * travel)
    thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_height)
    pygame.draw.rect(surface, COLORS["cyan"], thumb_rect, border_radius=track_rect.width // 2)
    return thumb_rect


def buy_upgrade_levels(upgrade_key, add_levels):
    global BULLET_SPEED, max_lives
    global damage_level, bullet_speed_level, live_level
    global damage_level_need_coin, bullet_speed_level_need_coin, live_level_need_coin
    global sentry_gun_level, tactical_support_level

    add_levels = upgrade_selection.clamp_addition(add_levels, add_levels)
    if add_levels <= 0:
        return False

    rows = {row["key"]: row for row in get_upgrade_rows()}
    row = rows.get(upgrade_key)
    if row is None:
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
        player.damage += add_levels
        damage_level += add_levels
        damage_level_need_coin = damage_level * row["cost_base"]
    elif upgrade_key == "bullet_speed":
        BULLET_SPEED += add_levels
        bullet_speed_level += add_levels
        bullet_speed_level_need_coin = bullet_speed_level * row["cost_base"]
    elif upgrade_key == "lives":
        max_lives += add_levels
        live_level += add_levels
        live_level_need_coin = live_level * row["cost_base"]
    elif upgrade_key == "sentry":
        sentry_gun_level += add_levels
        if not player.out_of_game:
            spawn_sentry_guns()
    elif upgrade_key == "tactical":
        tactical_support_level += add_levels

    autosave()
    return True


def upgrade_UI():
    upgrade_UI_running = True
    scroll_offset = 0
    row_height = 124
    viewport_rect = pygame.Rect(58, 165, 484, 510)
    scrollbar_rect = pygame.Rect(548, viewport_rect.y, 8, viewport_rect.height)
    back_button = pygame.Rect(180, 715, 240, 58)
    dragging_scrollbar = False
    drag_grab_dy = 0
    modal_row = None
    modal_selected_add = 0
    modal_max_add = 0
    modal_input_text = ""
    modal_input_active = False
    modal_caret = 0
    modal_select_all = False
    dragging_level_slider = False

    def sync_modal_value(value):
        nonlocal modal_selected_add, modal_input_text
        nonlocal modal_caret, modal_select_all
        modal_selected_add = upgrade_selection.clamp_addition(
            value,
            modal_max_add,
        )
        modal_input_text = str(modal_selected_add)
        modal_caret = len(modal_input_text)
        modal_select_all = False

    def update_modal_input_text(value, caret):
        nonlocal modal_selected_add, modal_input_text
        nonlocal modal_caret, modal_select_all
        modal_input_text = value
        modal_caret = clamp(caret, 0, len(modal_input_text))
        modal_select_all = False
        modal_selected_add = upgrade_selection.clamp_addition(
            modal_input_text,
            modal_max_add,
        )

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
        nonlocal modal_row, modal_selected_add, modal_max_add
        nonlocal modal_input_text, modal_input_active
        nonlocal modal_caret, modal_select_all
        nonlocal dragging_level_slider
        modal_row = None
        modal_selected_add = 0
        modal_max_add = 0
        modal_input_text = ""
        modal_input_active = False
        modal_caret = 0
        modal_select_all = False
        dragging_level_slider = False

    def confirm_modal_purchase():
        nonlocal modal_row, modal_max_add
        if modal_row is None:
            return False

        fresh_rows = {row["key"]: row for row in get_upgrade_rows()}
        fresh_row = fresh_rows.get(modal_row["key"])
        if fresh_row is None:
            return False

        fresh_max_add = upgrade_selection.max_affordable_addition(
            fresh_row["cost_base"],
            fresh_row["level"],
            player.coin,
            fresh_row["level_offset"],
        )
        modal_row = fresh_row
        modal_max_add = fresh_max_add
        if modal_selected_add > fresh_max_add:
            sync_modal_value(fresh_max_add)
            return False

        sync_modal_value(modal_input_text)
        total_cost = upgrade_selection.total_upgrade_cost(
            fresh_row["cost_base"],
            fresh_row["level"],
            modal_selected_add,
            fresh_row["level_offset"],
        )
        if modal_selected_add <= 0 or total_cost > player.coin:
            return False

        return buy_upgrade_levels(
            fresh_row["key"],
            modal_selected_add,
        )

    upgrade_background = ScrollingBackground(
        pygame.image.load('img/background/upgrade_background.jpg'),
        speed=2,
    )

    while upgrade_UI_running:
        upgrade_background.advance()
        upgrade_background.draw(screen)

        mx, my = pygame.mouse.get_pos()
        upgrade_rows = get_upgrade_rows()
        content_height = len(upgrade_rows) * row_height
        max_scroll = max(0, content_height - viewport_rect.height)
        scroll_offset = clamp(scroll_offset, 0, max_scroll)

        draw_panel(screen, pygame.Rect(45, 135, 510, 660), alpha=232)
        draw_heading(screen, 'Upgrade', 'SHIP SYSTEM ENHANCEMENT', y=76)
        draw_stat_card(
            screen,
            pygame.Rect(420, 45, 145, 64),
            'Coin',
            f'{player.coin:,}',
            accent=COLORS['gold'],
        )

        row_buttons = []
        previous_clip = screen.get_clip()
        screen.set_clip(viewport_rect)
        for index, row in enumerate(upgrade_rows):
            button = pygame.Rect(75, viewport_rect.y + index * row_height - scroll_offset, 450, 104)
            row_buttons.append((button, row))
            if not button.colliderect(viewport_rect):
                continue

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
        screen.set_clip(previous_clip)
        thumb_rect = draw_vertical_scrollbar(screen, scrollbar_rect, scroll_offset, max_scroll)

        draw_button(
            screen,
            back_button,
            'BACK TO MENU',
            hovered=back_button.collidepoint((mx, my)),
        )

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
                confirm_enabled=(
                    modal_selected_add > 0
                    and modal_total_cost <= player.coin
                ),
            )

        modal_event_barrier = modal_row is not None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if modal_event_barrier or modal_row is not None:
                if event.type == pygame.WINDOWFOCUSLOST:
                    dragging_level_slider = False
                if modal_row is None or modal_controls is None:
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        close_upgrade_modal()
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if confirm_modal_purchase():
                            close_upgrade_modal()
                    elif modal_input_active:
                        if event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
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
                        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                            if modal_select_all:
                                update_modal_input_text("", 0)
                            elif event.key == pygame.K_BACKSPACE and modal_caret > 0:
                                update_modal_input_text(
                                    modal_input_text[:modal_caret - 1]
                                    + modal_input_text[modal_caret:],
                                    modal_caret - 1,
                                )
                            elif (
                                event.key == pygame.K_DELETE
                                and modal_caret < len(modal_input_text)
                            ):
                                update_modal_input_text(
                                    modal_input_text[:modal_caret]
                                    + modal_input_text[modal_caret + 1:],
                                    modal_caret,
                                )
                        elif event.unicode and event.unicode.isdigit():
                            if modal_select_all:
                                updated_text = event.unicode
                                updated_caret = len(event.unicode)
                            else:
                                updated_text = (
                                    modal_input_text[:modal_caret]
                                    + event.unicode
                                    + modal_input_text[modal_caret:]
                                )
                                updated_caret = modal_caret + len(event.unicode)
                            update_modal_input_text(updated_text, updated_caret)
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if (
                        modal_input_active
                        and not modal_controls["input"].collidepoint(event.pos)
                    ):
                        modal_input_active = False
                        sync_modal_value(modal_input_text)

                    if modal_controls["cancel"].collidepoint(event.pos):
                        close_upgrade_modal()
                    elif modal_controls["confirm"].collidepoint(event.pos):
                        if confirm_modal_purchase():
                            close_upgrade_modal()
                    elif modal_controls["minus"].collidepoint(event.pos):
                        sync_modal_value(modal_selected_add - 1)
                    elif modal_controls["plus"].collidepoint(event.pos):
                        sync_modal_value(modal_selected_add + 1)
                    elif (
                        modal_max_add > 0
                        and (
                            modal_controls["slider"].inflate(0, 30).collidepoint(event.pos)
                            or modal_controls["slider_thumb"].collidepoint(event.pos)
                        )
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
                    elif modal_controls["input"].collidepoint(event.pos):
                        modal_input_active = True
                        modal_caret = clamp(
                            modal_caret,
                            0,
                            len(modal_input_text),
                        )
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging_level_slider = False
                elif event.type == pygame.MOUSEMOTION and dragging_level_slider:
                    if event.buttons[0]:
                        sync_modal_value(
                            upgrade_selection.slider_value_from_x(
                                event.pos[0],
                                modal_controls["slider"].left,
                                modal_controls["slider"].width,
                                modal_max_add,
                            )
                        )
                    else:
                        dragging_level_slider = False
                continue
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset = clamp(scroll_offset - event.y * 44, 0, max_scroll)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_offset = clamp(scroll_offset - 44, 0, max_scroll)
                if event.button == 5:
                    scroll_offset = clamp(scroll_offset + 44, 0, max_scroll)
                if event.button == 1:
                    if thumb_rect is not None and thumb_rect.collidepoint(event.pos):
                        dragging_scrollbar = True
                        drag_grab_dy = event.pos[1] - thumb_rect.y
                    else:
                        for button, row in row_buttons:
                            if viewport_rect.collidepoint(event.pos) and button.collidepoint(event.pos):
                                open_upgrade_modal(row)
                                break
                        if back_button.collidepoint(event.pos):
                            upgrade_UI_running = False
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_scrollbar = False
            if event.type == pygame.MOUSEMOTION:
                if dragging_scrollbar and thumb_rect is not None and max_scroll > 0:
                    travel = scrollbar_rect.height - thumb_rect.height
                    if travel > 0:
                        new_thumb_y = clamp(
                            event.pos[1] - drag_grab_dy,
                            scrollbar_rect.y,
                            scrollbar_rect.y + travel,
                        )
                        scroll_offset = clamp(
                            round((new_thumb_y - scrollbar_rect.y) / travel * max_scroll),
                            0,
                            max_scroll,
                        )

        pygame.display.update()
        clock.tick(60)

def credits():
    credits_running = True
    while credits_running:
        screen.fill(COLORS['navy'])
        mx, my = pygame.mouse.get_pos()
        button_1 = pygame.Rect(180, 790, 240, 58)
        draw_panel(screen, pygame.Rect(55, 130, 490, 630), alpha=240)
        draw_heading(screen, 'Credits', 'MISSION DEVELOPMENT CREW', y=72)

        credit_rows = (
            ('PROGRAMMER', 'LukeTseng'),
            ('GAME DESIGNER', 'LukeTseng'),
            ('GRAPH ARTIST / MATERIAL', 'FoozleCC'),
            ('BACKGROUND / MATERIAL', 'Leonardo AI'),
            ('MUSIC / MATERIAL', 'OpenGameArt : Oblidivm'),
            ('GAME ENGINE', 'Pygame'),
        )
        y = 190
        for role, name in credit_rows:
            draw_ui_text(screen, role, 14, COLORS['muted'], (SCREEN_WIDTH // 2, y))
            draw_ui_text(screen, name, 22, COLORS['text'], (SCREEN_WIDTH // 2, y + 28))
            y += 86

        draw_button(
            screen,
            button_1,
            'BACK',
            hovered=button_1.collidepoint((mx, my)),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint((mx, my)):
                        credits_running = False

        pygame.display.update()
        clock.tick(60)

def chose_level():
    global level
    chose_level_running = True
    level_buttons = level_grid_rects(SCREEN_WIDTH, SCREEN_HEIGHT)
    button_back = pygame.Rect(180, 790, 240, 58)
    while chose_level_running:
        screen.fill(COLORS['navy'])
        mx, my = pygame.mouse.get_pos()
        draw_panel(screen, pygame.Rect(35, 150, 530, 590), alpha=235)
        draw_heading(screen, 'Mission Select', 'NORMAL CAMPAIGN', y=72)
        for index, button in enumerate(level_buttons, start=1):
            unlocked = can_select_level(index, highest_unlocked_level)
            draw_button(
                screen,
                button,
                f'LEVEL {index:02d}',
                hovered=unlocked and button.collidepoint((mx, my)),
                style='secondary' if unlocked else 'locked',
                disabled=not unlocked,
            )

        draw_button(
            screen,
            button_back,
            'BACK',
            hovered=button_back.collidepoint((mx, my)),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, button in enumerate(level_buttons, start=1):
                    if button.collidepoint((mx, my)):
                        if can_select_level(i, highest_unlocked_level):
                            play_music("music/battle_in_the_stars.ogg")
                            config.is_enter_hard_mode = False
                            level = i
                            chose_level_running = False
                            player.out_of_game = False
                            reset_continue_game()
                            autosave()
                            break
                if button_back.collidepoint((mx, my)):
                    chose_level_running = False
                    main_menu()
        pygame.display.update()
        clock.tick(60)

def chose_hard_level():
    global hard_level, level
    chose_hard_level_running = True
    level_buttons = level_grid_rects(SCREEN_WIDTH, SCREEN_HEIGHT)
    button_back = pygame.Rect(180, 790, 240, 58)
    while chose_hard_level_running:
        screen.fill(COLORS['navy'])
        mx, my = pygame.mouse.get_pos()
        draw_heading(screen, 'Hard Missions', 'ELITE CAMPAIGN', y=72)
        if is_complete_game:
            draw_panel(screen, pygame.Rect(35, 150, 530, 590), alpha=235)
            for i, button in enumerate(level_buttons, start=1):
                unlocked = i <= hard_level
                draw_button(
                    screen,
                    button,
                    f'LEVEL {i:02d}',
                    hovered=unlocked and button.collidepoint((mx, my)),
                    style='danger' if unlocked else 'locked',
                    disabled=not unlocked,
                )
        else:
            draw_panel(screen, pygame.Rect(70, 260, 460, 300), alpha=242)
            draw_ui_text(
                screen,
                'ACCESS DENIED',
                30,
                COLORS['danger_hover'],
                (SCREEN_WIDTH // 2, 350),
            )
            draw_ui_text(
                screen,
                'Complete the normal campaign',
                19,
                COLORS['text'],
                (SCREEN_WIDTH // 2, 420),
            )
            draw_ui_text(
                screen,
                'to unlock elite missions.',
                19,
                COLORS['muted'],
                (SCREEN_WIDTH // 2, 455),
            )

        draw_button(
            screen,
            button_back,
            'BACK',
            hovered=button_back.collidepoint((mx, my)),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, button in enumerate(level_buttons, start=1):
                    if button.collidepoint((mx, my)):
                        if is_complete_game and i <= hard_level:
                            config.is_enter_hard_mode = True
                            level = i
                            chose_hard_level_running = False
                            player.out_of_game = False
                            reset_continue_game()
                            autosave()
                            break
                if button_back.collidepoint((mx, my)):
                    chose_hard_level_running = False
                    main_menu()
        pygame.display.update()
        clock.tick(60)

def chose_mode():
    chose_mode_running = True
    button_normal = pygame.Rect(155, 360, 290, 64)
    button_hard = pygame.Rect(155, 460, 290, 64)
    button_back = pygame.Rect(180, 620, 240, 58)
    while chose_mode_running:
        screen.fill(COLORS['navy'])
        mx, my = pygame.mouse.get_pos()
        draw_panel(screen, pygame.Rect(95, 210, 410, 500), alpha=235, border=COLORS['cyan'])
        draw_heading(screen, 'Select Mode', 'CHOOSE YOUR CAMPAIGN', y=110)
        draw_button(
            screen,
            button_normal,
            'NORMAL MODE',
            hovered=button_normal.collidepoint((mx, my)),
            style='primary',
        )
        draw_button(
            screen,
            button_hard,
            'HARD MODE',
            hovered=button_hard.collidepoint((mx, my)),
            style='danger',
        )
        draw_button(
            screen,
            button_back,
            'BACK',
            hovered=button_back.collidepoint((mx, my)),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_normal.collidepoint((mx, my)):
                    chose_mode_running = False
                    chose_level()
                if button_hard.collidepoint((mx, my)):
                    chose_mode_running = False
                    chose_hard_level()
                if button_back.collidepoint((mx, my)):
                    chose_mode_running = False
                    main_menu()
        pygame.display.update()
        clock.tick(60)

def main_menu():
    play_music("music/brave_pilots_menu_screen.ogg")
    main_running = True
    button_texts = ['Play', 'Upgrade', 'Setting', 'Exit', 'Credits']
    button_actions = [chose_mode, upgrade_UI, setting, sys.exit, credits]
    buttons = [
        pygame.Rect(155, 220 + i * 88, 290, 58)
        for i in range(len(button_texts))
    ]

    menu_background = ScrollingBackground(
        pygame.image.load('img/background/menu_background.jpg'),
        speed=2,
    )

    while main_running:
        menu_background.advance()
        menu_background.draw(screen)
        mx, my = pygame.mouse.get_pos()
        draw_panel(screen, pygame.Rect(115, 145, 370, 655), alpha=226, border=COLORS['cyan'])
        draw_heading(screen, 'Space Shooter', 'TACTICAL FLIGHT COMMAND', y=76)
        styles = ('primary', 'secondary', 'secondary', 'danger', 'secondary')
        for button, label, style in zip(buttons, button_texts, styles):
            draw_button(
                screen,
                button,
                label.upper(),
                hovered=button.collidepoint((mx, my)),
                style=style,
            )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for idx, button in enumerate(buttons):
                        if button.collidepoint((mx, my)):
                            if idx == 0:
                                main_running = False
                            button_actions[idx]()

        pygame.display.update()
        clock.tick(60)

def game_over_screen():
    play_music('music/defeated_game_over_tune.ogg')
    game_over_running = True
    player.out_of_game = True
    pygame.mouse.set_visible(True)
    result_background = screen.copy()
    button_return = pygame.Rect(125, 445, 350, 62)
    button_exit = pygame.Rect(125, 535, 350, 62)
    while game_over_running:
        screen.blit(result_background, (0, 0))
        mx, my = pygame.mouse.get_pos()
        modal = draw_modal_backdrop(screen, pygame.Rect(70, 225, 460, 450))
        draw_ui_text(screen, 'MISSION FAILED', 38, COLORS['danger_hover'], (modal.centerx, 315))
        draw_ui_text(
            screen,
            'Your ship has been destroyed.',
            18,
            COLORS['muted'],
            (modal.centerx, 375),
        )
        draw_button(
            screen,
            button_return,
            '1  /  RETURN TO COMMAND',
            hovered=button_return.collidepoint((mx, my)),
            style='primary',
        )
        draw_button(
            screen,
            button_exit,
            '2  /  EXIT GAME',
            hovered=button_exit.collidepoint((mx, my)),
            style='danger',
        )
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    main_menu()
                    game_over_running = False
                if event.key == pygame.K_2:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_return.collidepoint((mx, my)):
                    main_menu()
                    game_over_running = False
                if button_exit.collidepoint((mx, my)):
                    pygame.quit()
                    sys.exit()

def all_levels_completed_screen():
    play_music('music/victory_tune.ogg')
    all_levels_completed_running = True
    player.out_of_game = True
    pygame.mouse.set_visible(True)
    result_background = screen.copy()
    button_return = pygame.Rect(120, 520, 360, 64)
    while all_levels_completed_running:
        screen.blit(result_background, (0, 0))
        mx, my = pygame.mouse.get_pos()
        modal = draw_modal_backdrop(screen, pygame.Rect(60, 215, 480, 470))
        draw_ui_text(screen, 'CAMPAIGN COMPLETE', 34, COLORS['cyan_hover'], (modal.centerx, 305))
        draw_ui_text(
            screen,
            'All normal missions cleared.',
            19,
            COLORS['text'],
            (modal.centerx, 375),
        )
        draw_ui_text(
            screen,
            'Elite campaign access granted.',
            19,
            COLORS['gold'],
            (modal.centerx, 415),
        )
        draw_button(
            screen,
            button_return,
            '1  /  RETURN TO COMMAND',
            hovered=button_return.collidepoint((mx, my)),
            style='primary',
        )
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    main_menu()
                    all_levels_completed_running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_return.collidepoint((mx, my)):
                    main_menu()
                    all_levels_completed_running = False

def hard_campaign_completed_screen():
    play_music('music/victory_tune.ogg')
    hard_complete_running = True
    player.out_of_game = True
    pygame.mouse.set_visible(True)
    result_background = screen.copy()
    button_return = pygame.Rect(120, 520, 360, 64)
    while hard_complete_running:
        screen.blit(result_background, (0, 0))
        mx, my = pygame.mouse.get_pos()
        modal = draw_modal_backdrop(screen, pygame.Rect(60, 215, 480, 470))
        draw_ui_text(screen, 'ELITE CAMPAIGN COMPLETE', 28, COLORS['danger_hover'], (modal.centerx, 305))
        draw_ui_text(
            screen,
            'All elite missions cleared.',
            19,
            COLORS['text'],
            (modal.centerx, 375),
        )
        draw_ui_text(
            screen,
            'You are humanity\'s finest.',
            19,
            COLORS['gold'],
            (modal.centerx, 415),
        )
        draw_button(
            screen,
            button_return,
            '1  /  RETURN TO COMMAND',
            hovered=button_return.collidepoint((mx, my)),
            style='danger',
        )
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    main_menu()
                    hard_complete_running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_return.collidepoint((mx, my)):
                    main_menu()
                    hard_complete_running = False

def pause_menu():
    pause_running = True
    paused_background = screen.copy()
    button_1 = pygame.Rect(155, 365, 290, 62)
    button_2 = pygame.Rect(155, 460, 290, 62)
    button_3 = pygame.Rect(155, 555, 290, 62)
    while pause_running:
        screen.blit(paused_background, (0, 0))
        mx, my = pygame.mouse.get_pos()
        draw_modal_backdrop(screen, pygame.Rect(95, 210, 410, 500))
        draw_ui_text(screen, 'MISSION PAUSED', 34, COLORS['text'], (SCREEN_WIDTH // 2, 290))
        draw_button(
            screen,
            button_1,
            'CONTINUE',
            hovered=button_1.collidepoint((mx, my)),
            style='primary',
        )
        draw_button(
            screen,
            button_2,
            'SETTINGS',
            hovered=button_2.collidepoint((mx, my)),
        )
        draw_button(
            screen,
            button_3,
            'BACK TO MENU',
            hovered=button_3.collidepoint((mx, my)),
            style='danger',
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint((mx, my)):
                        pause_running = False
                        player.out_of_game = False
                    if button_2.collidepoint((mx, my)):
                        setting()
                    if button_3.collidepoint((mx, my)):
                        pause_running = False
                        main_menu()

        pygame.display.update()
        clock.tick(60)

def stage_clear_screen(level, score):
    stage_clear_running = True
    animation_score = 0
    animation_time = 0
    player.out_of_game = True
    pygame.mouse.set_visible(True)
    result_background = screen.copy()
    while stage_clear_running:
        screen.blit(result_background, (0, 0))
        draw_modal_backdrop(screen, pygame.Rect(65, 120, 470, 700))
        draw_ui_text(screen, 'MISSION COMPLETE', 34, COLORS['cyan_hover'], (SCREEN_WIDTH // 2, 205))
        draw_ui_text(screen, 'FINAL SCORE', 15, COLORS['muted'], (SCREEN_WIDTH // 2, 275))
        draw_ui_text(screen, f'{animation_score:,}', 34, COLORS['gold'], (SCREEN_WIDTH // 2, 320))

        if pygame.time.get_ticks() - animation_time > 5:
            if animation_score <= score:
                animation_score += 1
                animation_time = pygame.time.get_ticks()
        
        mx, my = pygame.mouse.get_pos()
        button_next_level = pygame.Rect(150, 390, 300, 58)
        button_restart_level = pygame.Rect(150, 470, 300, 58)
        button_back_menu = pygame.Rect(150, 690, 300, 58)
        draw_button(
            screen,
            button_next_level,
            'NEXT LEVEL',
            hovered=button_next_level.collidepoint((mx, my)),
            style='primary',
        )
        draw_button(
            screen,
            button_restart_level,
            'RESTART LEVEL',
            hovered=button_restart_level.collidepoint((mx, my)),
        )
        draw_button(
            screen,
            button_back_menu,
            'BACK TO MENU',
            hovered=button_back_menu.collidepoint((mx, my)),
            style='danger',
        )
        
        if level > 1:
            button_previous_level = pygame.Rect(150, 550, 300, 58)
            draw_button(
                screen,
                button_previous_level,
                'PREVIOUS LEVEL',
                hovered=button_previous_level.collidepoint((mx, my)),
            )
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if button_next_level.collidepoint((mx, my)):
                    # Enter Next level
                    if BOSS_GENERATION_ONCE["enemies_5"] or BOSS_GENERATION_ONCE["enemies_11"] or BOSS_GENERATION_ONCE["enemies_18"]:
                        play_music('music/battle_in_the_stars.ogg')
                    player.out_of_game = False
                    return 'next'
                if button_back_menu.collidepoint((mx, my)):
                    stage_clear_running = False
                    # Return menu
                    return 'menu'
                if level > 1 and button_previous_level.collidepoint((mx, my)):
                    # Return pervious level
                    if BOSS_GENERATION_ONCE["enemies_5"] or BOSS_GENERATION_ONCE["enemies_11"] or BOSS_GENERATION_ONCE["enemies_18"]:
                        play_music('music/battle_in_the_stars.ogg')
                    player.out_of_game = False
                    return 'previous'
                if button_restart_level.collidepoint((mx, my)):
                    # Restart current level
                    if BOSS_GENERATION_ONCE["enemies_5"] or BOSS_GENERATION_ONCE["enemies_11"] or BOSS_GENERATION_ONCE["enemies_18"]:
                        play_music('music/battle_in_the_stars.ogg')
                    player.out_of_game = False
                    return 'restart'

def check_bullet_hit(bullets, enemies, score_increment, drop_rate_1, drop_rate_2, Explosion, gain_coin=0):
    global score
    for bullet in bullets:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hit_enemies:
            hit_spark = HitSpark(bullet.rect.center)
            all_sprites.add(hit_spark)
            bullet.kill()
            if not enemy.invincible:
                enemy.hp -= getattr(bullet, "damage", player.damage)
                if enemy.hp <= 0:
                    boom_sound_effect.play()
                    player.coin += hard_mode.scale_coin(gain_coin, config.is_enter_hard_mode)
                    enemies.remove(enemy)
                    explosion = Explosion(enemy.rect.center)
                    all_sprites.add(explosion)
                    score += hard_mode.scale_kill_score(score_increment, config.is_enter_hard_mode)
                    if level >= 2:
                        if random.random() < drop_rate_1:
                            item1 = Item_1(enemy.rect.center)
                            items['item_1'].add(item1)
                            all_sprites.add(item1)
                    if level >= 4:
                        if random.random() < drop_rate_2:
                            item2 = Item_2(enemy.rect.center)
                            items['item_2'].add(item2)
                            all_sprites.add(item2)


def destroy_enemy_for_reward(enemy, score_increment, Explosion, gain_coin):
    global score
    if getattr(enemy, "hp", 1) <= 0:
        return

    boom_sound_effect.play()
    player.coin += hard_mode.scale_coin(gain_coin, config.is_enter_hard_mode)
    score += hard_mode.scale_kill_score(score_increment, config.is_enter_hard_mode)
    explosion = Explosion(enemy.rect.center)
    all_sprites.add(explosion)
    enemy.kill()


def destroy_tactical_support_targets_for_reward():
    destroyed = 0
    for group_key, score_increment, Explosion, gain_coin in TACTICAL_SUPPORT_REWARD_CONFIG:
        for enemy in enemies_p[group_key].sprites():
            destroy_enemy_for_reward(enemy, score_increment, Explosion, gain_coin)
            destroyed += 1
    return destroyed


def update_tactical_support():
    global tactical_support_last_trigger_time, tactical_support_effect_until, tactical_support_banner_until
    stats = support_upgrades.tactical_support_stats(tactical_support_level)
    if not stats["active"] or max_lives <= 0:
        return

    now = pygame.time.get_ticks()
    if support_upgrades.is_tactical_support_effect_active(now, tactical_support_effect_until):
        destroy_tactical_support_targets_for_reward()
        return

    if not support_upgrades.is_tactical_support_ready(
        now,
        tactical_support_last_trigger_time,
        stats["cooldown_ms"],
    ):
        return
    if player.lives / max_lives > stats["trigger_ratio"]:
        return

    tactical_support_effect_until = support_upgrades.tactical_support_active_until(now)
    tactical_support_last_trigger_time = now
    tactical_support_banner_until = now + 1800
    destroy_tactical_support_targets_for_reward()


def draw_tactical_support_banner(surface):
    if pygame.time.get_ticks() >= tactical_support_banner_until:
        return

    elapsed = tactical_support_banner_until - pygame.time.get_ticks()
    pulse = 1.0 if (elapsed // 120) % 2 == 0 else 0.65
    overlay = pygame.Surface((SCREEN_WIDTH, 118), pygame.SRCALPHA)
    overlay.fill((5, 14, 28, 165))
    surface.blit(overlay, (0, SCREEN_HEIGHT // 2 - 86))
    draw_ui_text(
        surface,
        "TACTICAL SUPPORT",
        42,
        COLORS["gold"],
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 42),
    )
    draw_ui_text(
        surface,
        "ORBITAL STRIKE AUTHORIZED",
        17,
        COLORS["cyan"] if pulse == 1.0 else COLORS["muted"],
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 4),
    )


def update_sentry_damage(enemy_groups):
    now = pygame.time.get_ticks()
    for sentry in sentry_guns.sprites():
        bullet_hits = pygame.sprite.spritecollide(sentry, enemy_bullets, True)
        if bullet_hits and sentry.take_damage(len(bullet_hits) * (level // 5 + 1), now):
            explode_sentry(sentry)
            continue

        for group, damage in enemy_groups:
            if pygame.sprite.spritecollideany(sentry, group):
                if sentry.take_damage(damage, now):
                    explode_sentry(sentry)
                break


def explode_sentry(sentry):
    explosion = Explosion_1(sentry.rect.center)
    all_sprites.add(explosion)
    sentry.kill()

def item_collision(player, item_type):
    hit_items = pygame.sprite.spritecollide(player, items[item_type], True)
    for item in hit_items:
        if item_type == 'item_1' and player.lives < max_lives:
            player.lives += 1
        elif item_type == 'item_2':
            player.activate_shield()          

def reset_enemies():
    for sprite in chain(*[enemies, *enemies_p.values(), enemy_bullets, items['item_1'], items['item_2']]):
        sprite.kill()
    
    BOSS_GENERATION_ONCE['enemies_5'] = False
    BOSS_GENERATION_ONCE['enemies_11'] = False
    BOSS_GENERATION_ONCE['enemies_18'] = False

last_spawn_time = 0

def generate_enemy(level, enemy_type, enemy_class, boss=False, Is_support=False):
    global last_spawn_time
    if boss:
        if not BOSS_GENERATION_ONCE[enemy_type]:
            boss = enemy_class()
            enemies_p[enemy_type].add(boss)
            all_sprites.add(boss)
            BOSS_GENERATION_ONCE[enemy_type] = True
            play_music('music/death_match_boss_theme.ogg')
    else:
        current_time = pygame.time.get_ticks()
        spawn_probability = hard_mode.scale_spawn_probability(
            ENEMY_GENERATION_THRESHOLDS[enemy_type], config.is_enter_hard_mode
        )
        if current_time - last_spawn_time >= 50 and random.random() < spawn_probability:
            enemy = enemy_class(enemies) if Is_support else enemy_class()
            enemies_p[enemy_type].add(enemy)
            all_sprites.add(enemy)
            if not Is_support:
                enemies.add(enemy)
            last_spawn_time = current_time

def get_active_boss():
    for boss_group_key in BOSS_GROUP_KEYS:
        for boss in enemies_p[boss_group_key]:
            if getattr(boss, "hp", 0) > 0:
                return boss
    return None


def display_text(text, value, color, position):
    rendered_text = font.render('{}: {}'.format(text, value), True, color)
    screen.blit(rendered_text, position)

def draw_opening_skip_prompt(skip_state):
    if skip_state.prompt_visible:
        draw_ui_opening_skip_prompt(screen, OPENING_SKIP_PROMPT)


def process_opening_events(skip_state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if is_opening_skip_input(
            event.type,
            pygame.KEYDOWN,
            pygame.MOUSEBUTTONDOWN,
        ) and skip_state.press_key():
            return True

    return False


def wait_during_opening(duration, skip_state, draw_frame):
    end_time = pygame.time.get_ticks() + duration
    while pygame.time.get_ticks() < end_time:
        if process_opening_events(skip_state):
            return True

        draw_frame()
        draw_opening_skip_prompt(skip_state)
        pygame.display.update()
        clock.tick(60)

    return False


def draw_opening_text(text, step, total_steps):
    draw_opening_briefing(
        screen,
        text,
        step,
        total_steps,
        pygame.time.get_ticks(),
    )


def display_text_word_by_word(text, step, total_steps, skip_state, delay=40):
    rendered_text = ''
    text_sound_effect.play()
    for word in text:
        rendered_text += word
        if wait_during_opening(
            delay,
            skip_state,
            lambda current_text=rendered_text: draw_opening_text(
                current_text,
                step,
                total_steps,
            ),
        ):
            text_sound_effect.stop()
            return True

    return False

def display_opening_screen(texts, delay=500):
    skip_state = OpeningSkipState()
    pygame.mixer.music.load('music/skyfire_title_screen.ogg')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.3)
    total_steps = len(texts)
    for step, text in enumerate(texts, start=1):
        if display_text_word_by_word(text, step, total_steps, skip_state):
            pygame.mixer.music.stop()
            return

        text_sound_effect.stop()
        if wait_during_opening(
            delay,
            skip_state,
            lambda current_text=text: draw_opening_text(
                current_text,
                step,
                total_steps,
            ),
        ):
            pygame.mixer.music.stop()
            return
    
    text_sound_effect.stop()
    creator_card = create_creator_card((440, 260))
    creator_rect = creator_card.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    for alpha in range(0, 256, 10):
        def draw_credit_fade_in(current_alpha=alpha):
            draw_tactical_starfield(screen, pygame.time.get_ticks())
            creator_card.set_alpha(current_alpha)
            screen.blit(creator_card, creator_rect)

        if wait_during_opening(100, skip_state, draw_credit_fade_in):
            pygame.mixer.music.stop()
            return
    
    def draw_credit():
        draw_tactical_starfield(screen, pygame.time.get_ticks())
        creator_card.set_alpha(255)
        screen.blit(creator_card, creator_rect)

    if wait_during_opening(3000, skip_state, draw_credit):
        pygame.mixer.music.stop()
        return

    for alpha in range(255, -1, -10):
        def draw_credit_fade_out(current_alpha=alpha):
            draw_tactical_starfield(screen, pygame.time.get_ticks())
            creator_card.set_alpha(current_alpha)
            screen.blit(creator_card, creator_rect)

        if wait_during_opening(100, skip_state, draw_credit_fade_out):
            pygame.mixer.music.stop()
            return

    if wait_during_opening(
        1000,
        skip_state,
        lambda: draw_tactical_starfield(screen, pygame.time.get_ticks()),
    ):
        pygame.mixer.music.stop()

texts = [
    'Earthlings from parallel universes', 
    'came to our current Earth.', 
    'Now, they are invading', 
    'and plundering our resources.', 
    'Enter the battleship, warrior.', 
    'We need your help and',
    'we can provide you with',
    'support and supplies',
    'You are the only hope',
    'for us people on earth.',
    'Go, you will be a hero.',
]

apply_save_state(save_manager.load_state())
atexit.register(autosave)

if not opening_seen:
    display_opening_screen(texts)
    opening_seen = True
    autosave()

main_menu()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.mouse.set_visible(True)
                pause_menu()
    
    if pygame.time.get_ticks() - level_start_time > hard_mode.scale_start_delay(3000, config.is_enter_hard_mode):
        if level < 6:
            generate_enemy(level, 'enemies_1', Enemy_1)
            if level > 1:
                generate_enemy(level, 'enemies_2', Enemy_2)
            if level > 2:
                generate_enemy(level, 'enemies_3', Enemy_3)
            if level > 3:
                generate_enemy(level, 'enemies_4', Enemy_4, Is_support=True)
            if level == 5:
                generate_enemy(level, 'enemies_5', Boss_1, boss=True)
        elif level > 5 and level <= 10:
            generate_enemy(level, 'enemies_6', Enemy_5)
            generate_enemy(level, 'enemies_7', Enemy_6)
            if level > 6:
                generate_enemy(level, 'enemies_8', Enemy_7)
            if level > 7:
                generate_enemy(level, 'enemies_9', Enemy_8, Is_support=True)
                generate_enemy(level, 'enemies_10', Enemy_9)
            if level == 10:
                generate_enemy(level, 'enemies_11', Boss_2, boss=True)
        elif level > 10:
            generate_enemy(level, 'enemies_12', Enemy_10)
            generate_enemy(level, 'enemies_13', Enemy_11)
            if level > 11:
                generate_enemy(level, 'enemies_14', Enemy_12)
                generate_enemy(level, 'enemies_15', Enemy_13)
            if level > 12:
                generate_enemy(level, 'enemies_16', Enemy_14, Is_support=True)
                generate_enemy(level, 'enemies_17', Enemy_15) 
            if level == 15:
                generate_enemy(level, 'enemies_18', Boss_3, boss=True)

    screen.fill((0, 0, 0))

    pressed_keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    all_sprites.update(pressed_keys, mouse_pos)

    if level <= len(backgrounds):
        active_background = backgrounds[level - 1]
        if gameplay_background.surface is not active_background:
            gameplay_background.set_surface(active_background)

    gameplay_background.advance()
    gameplay_background.draw(screen)

    for group in items.values():
        for item in group:
            screen.blit(item.surf, item.rect)

    for enemy_bullet in enemy_bullets:
        screen.blit(enemy_bullet.surf, enemy_bullet.rect)
    
    for group_key, score_increment, Explosion, gain_coin in ENEMY_REWARD_CONFIG:
        check_bullet_hit(
            bullets,
            enemies_p[group_key],
            score_increment,
            0.03,
            0.01,
            Explosion,
            gain_coin,
        )

    for item_type in items.keys():
        item_collision(player, item_type)

    enemy_damage_values = {
        'enemies_1': 1, 
        'enemies_2': 1, 
        'enemies_3': 2, 
        'enemies_4': 1, 
        'enemies_5': 5,
        'enemies_6': 1, 
        'enemies_7': 2, 
        'enemies_8': 3, 
        'enemies_9': 1, 
        'enemies_10': 3,
        'enemies_11': 5, 
        'enemies_12': 2,
        'enemies_13': 2,
        'enemies_14': 2,
        'enemies_15': 3,
        'enemies_16': 3,
        'enemies_17': 5,
        'enemies_18': 5,
    }

    enemy_damage_values = {
        key: hard_mode.scale_damage(damage, config.is_enter_hard_mode)
        for key, damage in enemy_damage_values.items()
    }

    enemy_groups = [(enemies_p[key], damage) for key, damage in enemy_damage_values.items()]
    for group, damage in enemy_groups:
        if pygame.sprite.spritecollideany(player, group):
            if not player.invincible and not player.invincible_shield:
                player.lives -= damage
                player.invincible = True
                player.last_hit_time = pygame.time.get_ticks()

    if pygame.sprite.spritecollideany(player, enemy_bullets):
        if not player.invincible and not player.invincible_shield:
            player.lives -= (level // 5 + 1)
            player.invincible = True 
            player.last_hit_time = pygame.time.get_ticks() 

    update_sentry_damage(enemy_groups)

    if player.invincible and pygame.time.get_ticks() - player.last_hit_time > 3000:
        player.invincible = False

    if player.invincible_shield and pygame.time.get_ticks() - player.shield_start_time > 5000:
        player.invincible_shield = False

    update_tactical_support()

    if player.lives <= 0:
        game_over_screen()
    
    if level > 15:
        if config.is_enter_hard_mode:
            hard_campaign_completed_screen()
        else:
            is_complete_game = True
            autosave()
            all_levels_completed_screen()

    if score > hard_mode.scale_clear_threshold(100 + (level * 10) * 9, config.is_enter_hard_mode): # 100 + (level * 10) * 9
        action = stage_clear_screen(level, score)
        if config.is_enter_hard_mode:
            hard_level = unlocked_level_after_clear(hard_level, level)
        else:
            highest_unlocked_level = unlocked_level_after_clear(highest_unlocked_level, level)
        autosave()
        if action == 'next':
            reset_enemies()
            level += 1
            score = 0
            player.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-30)
            player.lives = max_lives
            spawn_sentry_guns()
            reset_tactical_support_cooldown()
            level_start_time = pygame.time.get_ticks()
        elif action == 'menu':
            main_menu()
        elif action == 'previous':
            reset_enemies()
            level -= 1
            score = 0
            player.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-30)
            player.lives = max_lives
            spawn_sentry_guns()
            reset_tactical_support_cooldown()
            level_start_time = pygame.time.get_ticks() 
        elif action == 'restart':
            reset_enemies()
            score = 0
            player.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-30)
            player.lives = max_lives
            spawn_sentry_guns()
            reset_tactical_support_cooldown()
            level_start_time = pygame.time.get_ticks() 

    for entity in all_sprites:
        if entity == player:
            player.draw(screen)
        else:
            screen.blit(entity.surf, entity.rect)

    for entity in all_sprites:
        if isinstance(entity, Enemy) and entity.invincible:
            if entity.shield_surf is not None:
                screen.blit(entity.shield_surf, entity.shield_rect)

    draw_gameplay_hud(screen, level, score, player.lives, player.coin)
    draw_tactical_support_banner(screen)
    active_boss = get_active_boss()
    boss_health = boss_health_display.update(active_boss, pygame.time.get_ticks())
    if boss_health:
        draw_boss_health_bar(
            screen,
            boss_health.name,
            active_boss.hp,
            active_boss.maxhp,
            delayed_ratio=boss_health.delayed_ratio,
        )

    pygame.display.flip()
    clock.tick(180) 

pygame.quit()
sys.exit()
