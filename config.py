import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 600, 900
PLAYER_SPEED = 4
BULLET_SPEED = 25
ENEMY_GENERATION_THRESHOLDS = {
    'enemies_1': 0.02,
    'enemies_2': 0.005,
    'enemies_3': 0.005,
    'enemies_4': 0.003,
    'enemies_6': 0.02,
    'enemies_7': 0.005,
    'enemies_8': 0.005,
    'enemies_9': 0.003,
    'enemies_10': 0.0005,
    'enemies_12': 0.009,
    'enemies_13': 0.009,
    'enemies_14': 0.005,
    'enemies_15': 0.003,
    'enemies_16': 0.002,
    'enemies_17': 0.0006,
}

BOSS_GENERATION_ONCE = {
    'enemies_5': False,
    'enemies_11': False,
    'enemies_18': False,
}

max_lives = 90
player_bullet_angle = [5, 0, -5]
