from types import SimpleNamespace

import pygame

from bullet_collision import bullet_hits_enemy


def rect(left, top, width=6, height=32):
    return pygame.Rect(left, top, width, height)


def test_fast_bullet_hits_enemy_between_frames():
    bullet = SimpleNamespace(
        rect=rect(100, 100),
        previous_rect=rect(100, 500),
    )
    enemy = SimpleNamespace(rect=rect(98, 300, 12, 12))

    assert bullet_hits_enemy(bullet, enemy)
