from functools import lru_cache

import pygame

from config import BOSS_BAR_HEIGHT, GAMEPLAY_TOP, HUD_HEIGHT


COLORS = {
    "navy": (5, 12, 23),
    "panel": (10, 25, 40),
    "panel_light": (17, 43, 63),
    "border": (48, 91, 116),
    "cyan": (70, 211, 247),
    "cyan_hover": (139, 235, 255),
    "cyan_dark": (13, 88, 115),
    "text": (230, 246, 255),
    "muted": (133, 164, 183),
    "gold": (255, 203, 92),
    "danger": (185, 65, 76),
    "danger_hover": (231, 92, 103),
    "locked": (55, 70, 82),
    "locked_text": (106, 126, 139),
    "track": (20, 43, 58),
}

FONT_PATH = "font.ttf"


@lru_cache(maxsize=None)
def get_font(size):
    return pygame.font.Font(FONT_PATH, size)


def level_grid_rects(screen_width, screen_height):
    button_width = 150
    button_height = 58
    column_gap = 20
    row_gap = 18
    columns = 3
    rows = 5
    grid_width = button_width * columns + column_gap * (columns - 1)
    grid_height = button_height * rows + row_gap * (rows - 1)
    start_x = (screen_width - grid_width) // 2
    start_y = max(190, (screen_height - grid_height) // 2 - 10)

    return [
        pygame.Rect(
            start_x + column * (button_width + column_gap),
            start_y + row * (button_height + row_gap),
            button_width,
            button_height,
        )
        for row in range(rows)
        for column in range(columns)
    ]


def gameplay_hud_rects(screen_width):
    widths = (94, 124, 94, 124)
    gap = 6
    total_width = sum(widths) + gap * (len(widths) - 1)
    x = (screen_width - total_width) // 2
    rects = []

    for width in widths:
        rects.append(pygame.Rect(x, 8, width, HUD_HEIGHT - 16))
        x += width + gap

    return rects


def cut_corner_points(rect, cut=10):
    cut = max(0, min(cut, rect.width // 3, rect.height // 3))
    return [
        (rect.left + cut, rect.top),
        (rect.right, rect.top),
        (rect.right, rect.bottom - cut),
        (rect.right - cut, rect.bottom),
        (rect.left, rect.bottom),
        (rect.left, rect.top + cut),
    ]


def draw_text(
    surface,
    text,
    size,
    color,
    position,
    *,
    anchor="center",
):
    rendered = get_font(size).render(str(text), True, color)
    rect = rendered.get_rect()
    setattr(rect, anchor, position)
    surface.blit(rendered, rect)
    return rect


def draw_panel(
    surface,
    rect,
    *,
    fill=None,
    border=None,
    alpha=218,
    cut=12,
    border_width=2,
):
    rect = pygame.Rect(rect)
    fill = fill or COLORS["panel"]
    border = border or COLORS["border"]
    overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
    local_rect = overlay.get_rect()
    points = cut_corner_points(local_rect, cut)
    pygame.draw.polygon(overlay, (*fill, alpha), points)
    pygame.draw.lines(overlay, (*border, min(255, alpha + 25)), True, points, border_width)
    surface.blit(overlay, rect.topleft)
    return rect


def _button_colors(style, hovered, disabled):
    if disabled or style == "locked":
        return COLORS["locked"], COLORS["border"], COLORS["locked_text"]
    if style == "primary":
        fill = COLORS["cyan_dark"] if not hovered else (21, 119, 148)
        return fill, COLORS["cyan_hover"] if hovered else COLORS["cyan"], COLORS["text"]
    if style == "danger":
        fill = COLORS["danger_hover"] if hovered else COLORS["danger"]
        return fill, COLORS["danger_hover"], COLORS["text"]
    fill = COLORS["panel_light"] if hovered else COLORS["panel"]
    border = COLORS["cyan"] if hovered else COLORS["border"]
    return fill, border, COLORS["text"]


def draw_button(
    surface,
    rect,
    label,
    *,
    hovered=False,
    style="secondary",
    disabled=False,
    subtitle=None,
):
    rect = pygame.Rect(rect)
    fill, border, text_color = _button_colors(style, hovered, disabled)

    if hovered and not disabled:
        glow_rect = rect.inflate(8, 8)
        draw_panel(
            surface,
            glow_rect,
            fill=COLORS["navy"],
            border=border,
            alpha=110,
            cut=12,
            border_width=1,
        )

    draw_panel(surface, rect, fill=fill, border=border, alpha=238, cut=10)
    if subtitle:
        subtitle_lines = str(subtitle).splitlines()
        label_y = rect.centery - 18 if len(subtitle_lines) > 1 else rect.centery - 10
        draw_text(
            surface,
            label,
            21,
            text_color,
            (rect.left + 18, label_y),
            anchor="midleft",
        )
        for index, subtitle_line in enumerate(subtitle_lines):
            draw_text(
                surface,
                subtitle_line,
                14,
                COLORS["muted"] if not disabled else COLORS["locked_text"],
                (rect.left + 18, rect.centery + 10 + index * 18),
                anchor="midleft",
            )
    else:
        draw_text(surface, label, 22, text_color, rect.center)
    return rect


def draw_heading(surface, title, subtitle=None, *, y=88):
    draw_text(surface, title.upper(), 38, COLORS["text"], (surface.get_width() // 2, y))
    accent_width = min(260, max(100, len(title) * 13))
    pygame.draw.line(
        surface,
        COLORS["cyan"],
        (surface.get_width() // 2 - accent_width // 2, y + 31),
        (surface.get_width() // 2 + accent_width // 2, y + 31),
        2,
    )
    if subtitle:
        draw_text(
            surface,
            subtitle,
            16,
            COLORS["muted"],
            (surface.get_width() // 2, y + 55),
        )


def draw_stat_card(surface, rect, label, value, *, accent=None):
    rect = pygame.Rect(rect)
    accent = accent or COLORS["cyan"]
    draw_panel(surface, rect, alpha=225, cut=8, border=accent, border_width=1)
    pygame.draw.line(
        surface,
        accent,
        (rect.left + 1, rect.top + 7),
        (rect.left + 1, rect.bottom - 2),
        3,
    )
    draw_text(
        surface,
        label.upper(),
        10,
        COLORS["muted"],
        (rect.left + 12, rect.top + 11),
        anchor="midleft",
    )
    draw_text(
        surface,
        value,
        18,
        accent if label.lower() == "coin" else COLORS["text"],
        (rect.left + 12, rect.bottom - 12),
        anchor="midleft",
    )
    return rect


def draw_gameplay_hud(surface, level, score, lives, coin):
    values = (
        ("Level", level, COLORS["cyan"]),
        ("Score", f"{score:,}", COLORS["cyan"]),
        ("Lives", lives, COLORS["cyan_hover"]),
        ("Coin", f"{coin:,}", COLORS["gold"]),
    )
    rects = gameplay_hud_rects(surface.get_width())
    for rect, (label, value, accent) in zip(rects, values):
        draw_stat_card(surface, rect, label, value, accent=accent)
    return rects


def boss_health_bar_rect(screen_width):
    width = min(screen_width - 42, 540)
    return pygame.Rect((screen_width - width) // 2, HUD_HEIGHT, width, BOSS_BAR_HEIGHT)


def boss_health_color(ratio):
    ratio = max(0.0, min(1.0, ratio))
    if ratio < 0.2:
        return COLORS["danger"]
    if ratio < 0.6:
        return COLORS["gold"]
    return COLORS["cyan"]


def draw_boss_health_bar(surface, name, current, maximum, delayed_ratio=0.0):
    from boss_health import health_ratio

    ratio = health_ratio(current, maximum)
    delayed_ratio = max(ratio, min(1.0, delayed_ratio))
    rect = boss_health_bar_rect(surface.get_width())
    draw_panel(surface, rect, alpha=210, cut=7, border=COLORS["danger"], border_width=1)

    draw_text(
        surface,
        name,
        13,
        COLORS["text"],
        (rect.left + 14, rect.centery),
        anchor="midleft",
    )
    draw_text(
        surface,
        f"{round(ratio * 100):03d}%",
        13,
        COLORS["danger_hover"],
        (rect.right - 14, rect.centery),
        anchor="midright",
    )

    track = pygame.Rect(rect.left + 150, rect.top + 10, rect.width - 220, 10)
    pygame.draw.rect(surface, COLORS["track"], track, border_radius=track.height // 2)

    if delayed_ratio > ratio:
        delayed = track.copy()
        delayed.width = round(track.width * delayed_ratio)
        pygame.draw.rect(
            surface,
            COLORS["danger_hover"],
            delayed,
            border_radius=track.height // 2,
        )

    if ratio > 0:
        fill = track.copy()
        fill.width = max(2, round(track.width * ratio))
        pygame.draw.rect(
            surface,
            boss_health_color(ratio),
            fill,
            border_radius=track.height // 2,
        )

    pygame.draw.rect(surface, COLORS["border"], track, 2, border_radius=track.height // 2)
    return rect


def draw_slider(surface, rect, value):
    rect = pygame.Rect(rect)
    value = max(0.0, min(1.0, value))
    pygame.draw.rect(surface, COLORS["track"], rect, border_radius=rect.height // 2)
    fill_rect = rect.copy()
    fill_rect.width = max(rect.height, round(rect.width * value))
    pygame.draw.rect(surface, COLORS["cyan"], fill_rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, COLORS["border"], rect, 2, border_radius=rect.height // 2)

    handle = pygame.Rect(0, 0, rect.height + 14, rect.height + 14)
    handle.center = (rect.left + round(rect.width * value), rect.centery)
    pygame.draw.circle(surface, COLORS["panel"], handle.center, handle.width // 2)
    pygame.draw.circle(surface, COLORS["cyan_hover"], handle.center, handle.width // 2, 3)
    return handle


def draw_modal_backdrop(surface, rect=None):
    shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shade.fill((*COLORS["navy"], 210))
    surface.blit(shade, (0, 0))
    if rect is None:
        rect = pygame.Rect(70, 170, surface.get_width() - 140, surface.get_height() - 340)
    draw_panel(surface, rect, alpha=242, cut=16, border=COLORS["cyan"])
    return pygame.Rect(rect)


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


def draw_tactical_starfield(surface, tick):
    surface.fill(COLORS["navy"])
    width, height = surface.get_size()
    drift = tick // 35

    for index in range(72):
        x = (index * 83 + 29) % width
        y = (index * 137 + drift * (1 + index % 3)) % height
        brightness = 95 + (index * 31) % 130
        radius = 2 if index % 11 == 0 else 1
        pygame.draw.circle(
            surface,
            (brightness, min(255, brightness + 25), 255),
            (x, y),
            radius,
        )

    glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(
        glow,
        (*COLORS["cyan_dark"], 38),
        (width // 2, height // 2),
        min(width, height) // 2,
    )
    surface.blit(glow, (0, 0))
    return surface.get_rect()


def draw_opening_briefing(surface, text, step, total_steps, tick):
    draw_tactical_starfield(surface, tick)
    width, height = surface.get_size()
    panel = pygame.Rect(55, 255, width - 110, 360)
    draw_panel(surface, panel, alpha=236, cut=16, border=COLORS["cyan"])

    draw_text(surface, "MISSION BRIEFING", 28, COLORS["text"], (width // 2, 105))
    draw_text(
        surface,
        "SECURE CHANNEL // EARTH COMMAND",
        14,
        COLORS["cyan"],
        (width // 2, 145),
    )
    pygame.draw.line(
        surface,
        COLORS["border"],
        (95, 180),
        (width - 95, 180),
        1,
    )

    scan_y = panel.top + 22 + (tick // 12) % (panel.height - 44)
    scan_layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.line(
        scan_layer,
        (*COLORS["cyan"], 55),
        (panel.left + 18, scan_y),
        (panel.right - 18, scan_y),
        2,
    )
    surface.blit(scan_layer, (0, 0))

    draw_text(
        surface,
        "INCOMING TRANSMISSION",
        13,
        COLORS["muted"],
        (panel.left + 30, panel.top + 45),
        anchor="midleft",
    )
    draw_text(
        surface,
        text,
        24,
        COLORS["text"],
        panel.center,
    )

    safe_total = max(1, total_steps)
    safe_step = max(1, min(step, safe_total))
    progress_rect = pygame.Rect(panel.left + 30, panel.bottom - 62, panel.width - 60, 8)
    pygame.draw.rect(surface, COLORS["track"], progress_rect, border_radius=4)
    fill_rect = progress_rect.copy()
    fill_rect.width = max(8, round(progress_rect.width * safe_step / safe_total))
    pygame.draw.rect(surface, COLORS["cyan"], fill_rect, border_radius=4)
    draw_text(
        surface,
        f"PACKET {safe_step:02d} / {safe_total:02d}",
        13,
        COLORS["muted"],
        (panel.right - 30, panel.bottom - 28),
        anchor="midright",
    )
    return panel


def draw_opening_skip_prompt(surface, prompt):
    rect = pygame.Rect(115, surface.get_height() - 86, surface.get_width() - 230, 44)
    draw_panel(surface, rect, alpha=226, cut=8, border=COLORS["cyan"], border_width=1)
    draw_text(surface, prompt, 14, COLORS["cyan_hover"], rect.center)
    return rect


def create_creator_card(size):
    card = pygame.Surface(size, pygame.SRCALPHA)
    rect = card.get_rect().inflate(-4, -4)
    draw_panel(card, rect, alpha=242, cut=16, border=COLORS["cyan"])
    draw_text(card, "DEVELOPED BY", 15, COLORS["muted"], (rect.centerx, 58))
    draw_text(card, "LukeTseng", 36, COLORS["text"], (rect.centerx, 118))
    pygame.draw.line(
        card,
        COLORS["cyan"],
        (rect.left + 70, 157),
        (rect.right - 70, 157),
        2,
    )
    draw_text(card, "PYGAME EDITION", 15, COLORS["cyan"], (rect.centerx, 198))
    return card
