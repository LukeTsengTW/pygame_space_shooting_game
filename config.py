import pygame

pygame.mixer.init()

volume_level = 0.5

pygame.mixer.music.set_volume(volume_level)

def play_music(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(-1)

SCREEN_WIDTH, SCREEN_HEIGHT = 600, 900
PLAYER_SPEED = 4
BULLET_SPEED = 25
ENEMY_GENERATION_THRESHOLDS = {
    'enemies_1': 0.05,
    'enemies_2': 0.01,
    'enemies_3': 0.02,
    'enemies_4': 0.01,
    'enemies_6': 0.05,
    'enemies_7': 0.01,
    'enemies_8': 0.01,
    'enemies_9': 0.02,
    'enemies_10': 0.002,
    'enemies_12': 0.009,
    'enemies_13': 0.009,
    'enemies_14': 0.005,
    'enemies_15': 0.005,
    'enemies_16': 0.002,
    'enemies_17': 0.002,
}

BOSS_GENERATION_ONCE = {
    'enemies_5': False,
    'enemies_11': False,
    'enemies_18': False,
}

max_lives = 90
player_bullet_angle = [5, 0, -5]

enemy_hp = {
    'enemies_1': 100,
    'enemies_2': 600,
    'enemies_3': 300,
    'enemies_4': 200,
    'enemies_5': 50000,
    'enemies_6': 500,
    'enemies_7': 1500,
    'enemies_8': 1000,
    'enemies_9': 1000,
    'enemies_10': 4000,
    'enemies_11': 200000,
    'enemies_12': 2000,
    'enemies_13': 1500,
    'enemies_14': 3000,
    'enemies_15': 1500,
    'enemies_16': 2000,
    'enemies_17': 6000,
    'enemies_18': 300000,
}

