import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from ui import (
    COLORS,
    boss_health_bar_rect,
    boss_health_color,
    create_creator_card,
    draw_boss_health_bar,
    draw_button,
    draw_gameplay_hud,
    draw_opening_briefing,
    draw_opening_skip_prompt,
    draw_panel,
    draw_slider,
    draw_tactical_starfield,
    draw_upgrade_level_modal,
    gameplay_hud_rects,
    level_grid_rects,
    upgrade_level_modal_rects,
)
from config import GAMEPLAY_TOP, HUD_HEIGHT


class TacticalUiGeometryTests(unittest.TestCase):
    def test_level_grid_has_fifteen_unique_in_bounds_buttons(self):
        rects = level_grid_rects(600, 900)

        self.assertEqual(len(rects), 15)
        self.assertEqual(len({tuple(rect) for rect in rects}), 15)
        self.assertEqual(len({rect.x for rect in rects}), 3)
        self.assertTrue(all(pygame.Rect(0, 0, 600, 900).contains(rect) for rect in rects))

    def test_gameplay_hud_cards_are_in_bounds_and_do_not_overlap(self):
        rects = gameplay_hud_rects(600)

        self.assertEqual(len(rects), 4)
        self.assertTrue(all(pygame.Rect(0, 0, 600, 900).contains(rect) for rect in rects))
        self.assertTrue(all(rect.top >= 0 and rect.bottom <= HUD_HEIGHT for rect in rects))
        for index, rect in enumerate(rects):
            for other in rects[index + 1:]:
                self.assertFalse(rect.colliderect(other))

    def test_boss_health_bar_sits_below_gameplay_hud(self):
        boss_rect = boss_health_bar_rect(600)
        hud_bottom = max(rect.bottom for rect in gameplay_hud_rects(600))

        self.assertTrue(pygame.Rect(0, 0, 600, 900).contains(boss_rect))
        self.assertGreater(boss_rect.top, hud_bottom)
        self.assertGreaterEqual(boss_rect.top, HUD_HEIGHT)
        self.assertLessEqual(boss_rect.bottom, GAMEPLAY_TOP)

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


class TacticalUiRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.surface = pygame.Surface((600, 900), pygame.SRCALPHA)

    def test_panel_draws_translucent_surface_and_border(self):
        draw_panel(self.surface, pygame.Rect(50, 50, 300, 180))

        self.assertNotEqual(self.surface.get_at((60, 60)), pygame.Color(0, 0, 0, 0))
        self.assertNotEqual(self.surface.get_at((200, 120)), pygame.Color(0, 0, 0, 0))

    def test_button_semantic_styles_render_distinct_pixels(self):
        rect = pygame.Rect(100, 100, 260, 58)
        samples = {}

        for style in ("primary", "secondary", "danger", "locked"):
            surface = pygame.Surface((600, 900), pygame.SRCALPHA)
            draw_button(
                surface,
                rect,
                style.title(),
                hovered=style != "locked",
                style=style,
                disabled=style == "locked",
            )
            samples[style] = tuple(surface.get_at((rect.left + 24, rect.centery)))

        self.assertEqual(len(set(samples.values())), 4)
        self.assertGreater(samples["primary"][2], samples["primary"][0])
        self.assertGreater(samples["danger"][0], samples["danger"][2])

    def test_gameplay_hud_renders_all_four_cards(self):
        rects = gameplay_hud_rects(600)

        draw_gameplay_hud(self.surface, 15, 8420, 92, 1280)

        for rect in rects:
            self.assertNotEqual(
                self.surface.get_at((rect.x + 8, rect.y + 8)),
                pygame.Color(0, 0, 0, 0),
            )

    def test_boss_health_color_thresholds_match_tactical_states(self):
        self.assertEqual(boss_health_color(0.8), COLORS["cyan"])
        self.assertEqual(boss_health_color(0.5), COLORS["gold"])
        self.assertEqual(boss_health_color(0.19), COLORS["danger"])

    def test_boss_health_bar_renders_name_percent_and_damage_trail(self):
        rect = draw_boss_health_bar(
            self.surface,
            "EARTH DESTROYER",
            400,
            1000,
            delayed_ratio=0.7,
        )

        self.assertTrue(pygame.Rect(0, 0, 600, 900).contains(rect))
        self.assertNotEqual(self.surface.get_at(rect.center), pygame.Color(0, 0, 0, 0))
        fill_y = rect.top + 15
        self.assertEqual(self.surface.get_at((rect.left + 170, fill_y))[:3], COLORS["gold"])
        self.assertNotEqual(
            self.surface.get_at((rect.left + round(rect.width * 0.65), fill_y)),
            pygame.Color(0, 0, 0, 0),
        )

    def test_boss_health_bar_handles_zero_health(self):
        rect = draw_boss_health_bar(
            self.surface,
            "VOID CRUISER",
            0,
            1000,
            delayed_ratio=0.0,
        )

        self.assertTrue(pygame.Rect(0, 0, 600, 900).contains(rect))
        self.assertNotEqual(self.surface.get_at((rect.left + 18, rect.top + 18)), pygame.Color(0, 0, 0, 0))

    def test_slider_clamps_fill_to_track(self):
        rect = pygame.Rect(120, 300, 360, 18)

        handle = draw_slider(self.surface, rect, 2.0)

        self.assertLessEqual(handle.right, rect.right + handle.width // 2)
        self.assertEqual(handle.centerx, rect.right)
        fill_sample_x = rect.right - handle.width
        self.assertEqual(
            self.surface.get_at((fill_sample_x, rect.centery))[:3],
            COLORS["cyan"],
        )

    def test_tactical_starfield_is_deterministic_for_same_tick(self):
        first = pygame.Surface((600, 900), pygame.SRCALPHA)
        second = pygame.Surface((600, 900), pygame.SRCALPHA)

        draw_tactical_starfield(first, 1234)
        draw_tactical_starfield(second, 1234)

        self.assertEqual(
            pygame.image.tostring(first, "RGBA"),
            pygame.image.tostring(second, "RGBA"),
        )

    def test_opening_briefing_supports_first_and_final_steps(self):
        first = pygame.Surface((600, 900), pygame.SRCALPHA)
        final = pygame.Surface((600, 900), pygame.SRCALPHA)

        first_rect = draw_opening_briefing(first, "Incoming transmission", 1, 11, 500)
        final_rect = draw_opening_briefing(final, "Go, you will be a hero.", 11, 11, 500)

        self.assertTrue(pygame.Rect(0, 0, 600, 900).contains(first_rect))
        self.assertTrue(pygame.Rect(0, 0, 600, 900).contains(final_rect))
        self.assertNotEqual(first.get_at(first_rect.center), pygame.Color(0, 0, 0, 0))
        self.assertNotEqual(final.get_at(final_rect.center), pygame.Color(0, 0, 0, 0))

    def test_opening_skip_prompt_draws_status_strip(self):
        rect = draw_opening_skip_prompt(
            self.surface,
            "PRESS ANY KEY AGAIN TO SKIP",
        )

        self.assertTrue(pygame.Rect(0, 0, 600, 900).contains(rect))
        self.assertNotEqual(self.surface.get_at(rect.center), pygame.Color(0, 0, 0, 0))

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
            confirm_enabled=True,
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

    def test_upgrade_level_modal_clips_long_active_input_text(self):
        baseline = pygame.Surface((600, 900), pygame.SRCALPHA)
        long_input = pygame.Surface((600, 900), pygame.SRCALPHA)
        common = {
            "current_level": 3,
            "selected_add": 9,
            "max_add": 9,
            "total_cost": 66_651,
            "input_active": True,
            "mouse_pos": (0, 0),
            "confirm_enabled": True,
        }

        baseline_controls = draw_upgrade_level_modal(
            baseline,
            "WEAPON DAMAGE",
            input_text="",
            **common,
        )
        long_controls = draw_upgrade_level_modal(
            long_input,
            "WEAPON DAMAGE",
            input_text="1234567890" * 8,
            **common,
        )

        input_rect = long_controls["input"]
        self.assertEqual(input_rect, baseline_controls["input"])
        left_sample = pygame.Rect(
            input_rect.left - 100,
            input_rect.top,
            100,
            input_rect.height,
        )
        right_sample = pygame.Rect(
            input_rect.right,
            input_rect.top,
            100,
            input_rect.height,
        )
        for sample in (left_sample, right_sample):
            self.assertEqual(
                pygame.image.tostring(baseline.subsurface(sample), "RGBA"),
                pygame.image.tostring(long_input.subsurface(sample), "RGBA"),
            )

    def test_upgrade_level_modal_disables_controls_at_zero(self):
        zero_surface = pygame.Surface((600, 900), pygame.SRCALPHA)
        enabled_surface = pygame.Surface((600, 900), pygame.SRCALPHA)

        zero_controls = draw_upgrade_level_modal(
            zero_surface,
            "SENTRY GUN",
            current_level=0,
            selected_add=0,
            max_add=0,
            total_cost=0,
            input_text="0",
            input_active=False,
            mouse_pos=(0, 0),
            confirm_enabled=False,
        )
        enabled_controls = draw_upgrade_level_modal(
            enabled_surface,
            "SENTRY GUN",
            current_level=0,
            selected_add=1,
            max_add=2,
            total_cost=50_000,
            input_text="1",
            input_active=False,
            mouse_pos=(0, 0),
            confirm_enabled=True,
        )

        self.assertEqual(
            zero_controls["slider_thumb"].centerx,
            zero_controls["slider"].left,
        )
        self.assertTrue(zero_controls["modal"].contains(zero_controls["confirm"]))
        for name in ("minus", "plus", "confirm"):
            zero_sample = (zero_controls[name].left + 12, zero_controls[name].centery)
            enabled_sample = (
                enabled_controls[name].left + 12,
                enabled_controls[name].centery,
            )
            self.assertNotEqual(
                zero_surface.get_at(zero_sample)[:3],
                enabled_surface.get_at(enabled_sample)[:3],
            )

    def test_upgrade_level_modal_honors_explicit_confirm_enabled_state(self):
        disabled_surface = pygame.Surface((600, 900), pygame.SRCALPHA)
        enabled_surface = pygame.Surface((600, 900), pygame.SRCALPHA)
        disabled_controls = draw_upgrade_level_modal(
            disabled_surface,
            "SENTRY GUN",
            current_level=0,
            selected_add=1,
            max_add=2,
            total_cost=50_000,
            input_text="1",
            input_active=False,
            mouse_pos=(0, 0),
            confirm_enabled=False,
        )
        enabled_controls = draw_upgrade_level_modal(
            enabled_surface,
            "SENTRY GUN",
            current_level=0,
            selected_add=1,
            max_add=2,
            total_cost=50_000,
            input_text="1",
            input_active=False,
            mouse_pos=(0, 0),
            confirm_enabled=True,
        )

        disabled_sample = (
            disabled_controls["confirm"].left + 12,
            disabled_controls["confirm"].centery,
        )
        enabled_sample = (
            enabled_controls["confirm"].left + 12,
            enabled_controls["confirm"].centery,
        )
        self.assertNotEqual(
            disabled_surface.get_at(disabled_sample)[:3],
            enabled_surface.get_at(enabled_sample)[:3],
        )

    def test_creator_card_has_visible_alpha_content(self):
        card = create_creator_card((440, 260))

        self.assertEqual(card.get_size(), (440, 260))
        self.assertGreater(pygame.mask.from_surface(card).count(), 0)


if __name__ == "__main__":
    unittest.main()
