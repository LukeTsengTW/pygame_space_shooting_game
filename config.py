import pygame

is_enter_hard_mode = False

pygame.mixer.init()

volume_level = 0.5

pygame.mixer.music.set_volume(volume_level)

text_sound_effect = pygame.mixer.Sound('sound_effect/text_sound_effect.mp3')
boom_sound_effect = pygame.mixer.Sound('sound_effect/boom.mp3')
boom_sound_effect.set_volume(0.2)
laser_sound_effect = pygame.mixer.Sound('sound_effect/laser.mp3')
laser_sound_effect.set_volume(0.2)

def play_music(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(-1)

SCREEN_WIDTH, SCREEN_HEIGHT = 600, 900
PLAYER_SPEED = 4
BULLET_SPEED = 20
ENEMY_GENERATION_THRESHOLDS = {
    'enemies_1': 0.05,
    'enemies_2': 0.02,
    'enemies_3': 0.02,
    'enemies_4': 0.009,
    'enemies_6': 0.05,
    'enemies_7': 0.02,
    'enemies_8': 0.02,
    'enemies_9': 0.009,
    'enemies_10': 0.001,
    'enemies_12': 0.009,
    'enemies_13': 0.009,
    'enemies_14': 0.005,
    'enemies_15': 0.005,
    'enemies_16': 0.002,
    'enemies_17': 0.001,
}

BOSS_GENERATION_ONCE = {
    'enemies_5': False,
    'enemies_11': False,
    'enemies_18': False,
}

max_lives = 100
player_bullet_angle = [5, 0, -5]

enemy_hp = {
    'enemies_1': 600,
    'enemies_2': 1000,
    'enemies_3': 800,
    'enemies_4': 600,
    'enemies_5': 50000,
    'enemies_6': 1200,
    'enemies_7': 2500,
    'enemies_8': 1800,
    'enemies_9': 1200,
    'enemies_10': 5000,
    'enemies_11': 200000,
    'enemies_12': 2400,
    'enemies_13': 3500,
    'enemies_14': 3800,
    'enemies_15': 1500,
    'enemies_16': 2000,
    'enemies_17': 7000,
    'enemies_18': 300000,
}

