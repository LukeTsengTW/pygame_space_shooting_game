import sys
import random
from itertools import chain
from config import *
from enemy import Enemy, Enemy_1, Enemy_2, Enemy_3, Enemy_4, Enemy_5, Enemy_6, Enemy_7, Enemy_8, Enemy_9, Enemy_10, Enemy_11, Enemy_12, Enemy_13, Enemy_14, Enemy_15, Boss_1, Boss_2, Boss_3
from item import Item_1, Item_2
from explosion import Explosion_1, Explosion_2, Explosion_3, Explosion_4, Explosion_5, Explosion_6, Explosion_7, Explosion_8, Explosion_9, Explosion_10, Explosion_11, Explosion_12, Explosion_13, Explosion_14, Explosion_15, Explosion_16, Explosion_17, Explosion_18
from player import Player
from shared import enemy_bullets, enemies, all_sprites, bullets

items = {
    'item_1': pygame.sprite.Group(),
    'item_2': pygame.sprite.Group(),
}
enemies_p = {f"enemies_{i}": pygame.sprite.Group() for i in range(1, 19)}

level_start_time = 0

damage_level = 0
damage_level_need_coin = 0
bullet_speed_level = 0
bullet_speed_level_need_coin = 0
live_level = 0
live_level_need_coin = 0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_icon(pygame.image.load('icon.png'))
pygame.display.set_caption('Space Shooter - Pygame Edition v1.0 - By: @LukeTseng')
font = pygame.font.Font('font.ttf', 36)
clock = pygame.time.Clock()

hard_level = 1
level = 1

is_complete_game = False

backgrounds = [pygame.image.load(f'img/background/lv{i}_background.jpg') for i in range(1, 21)]
background = backgrounds[0]
background_bottom = backgrounds[0]
background_rect = background.get_rect()
background_rect_bottom = background_bottom.get_rect()
background_rect_bottom.top = background_rect.bottom

score = 0 
running = True 

player = Player()
all_sprites.add(player)

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def reset_game():
    for sprite in all_sprites:
        sprite.kill()

    all_sprites.add(player)
    player.lives = max_lives
    global score, level, level_start_time
    score, level = 0, 1
    level_start_time = pygame.time.get_ticks()

def reset_continue_game():
    for sprite in all_sprites:
        sprite.kill()

    all_sprites.add(player)
    player.lives = max_lives
    global score, level_start_time
    score = 0
    level_start_time = pygame.time.get_ticks()

current_text = 0 
def setting():
    global current_text, volume_level
    setting_running = True
    text_options = ['Control the sprite with keyboard', 'Control the sprite with cursor']

    button_width = 200
    button_height = 50
    button_1 = pygame.Rect((SCREEN_WIDTH - 550) // 2, (SCREEN_HEIGHT - button_height) // 2 - 180, 550, button_height)
    button_2 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 60, button_width, button_height)

    background = pygame.image.load(f'img/background/setting_background.jpg')
    background_bottom = background
    background_rect = background.get_rect()
    background_rect_bottom = background_bottom.get_rect()
    background_rect_bottom.top = background_rect.bottom

    while setting_running:
        background_rect.move_ip(0, 2)
        background_rect_bottom.move_ip(0, 2)
        if background_rect.top >= SCREEN_HEIGHT:
            background_rect.bottom = background_rect_bottom.top
        if background_rect_bottom.top >= SCREEN_HEIGHT:
            background_rect_bottom.bottom = background_rect.top

        screen.blit(background, background_rect)
        screen.blit(background_bottom, background_rect_bottom)

        draw_text('Setting', font, (255, 255, 255), screen, SCREEN_WIDTH/2, 150)

        mx, my = pygame.mouse.get_pos()
        
        pygame.draw.rect(screen, (0, 200, 0), button_1)
        pygame.draw.rect(screen, (200, 0, 0), button_2)

        text = text_options[current_text]
        draw_text(text , font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180)
        draw_text('Back menu', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)

        # Add a slider for volume control
        slider_rect = pygame.Rect((SCREEN_WIDTH - 300) // 2, SCREEN_HEIGHT // 2 - 60, 300, 20)
        slider_button_rect = pygame.Rect((SCREEN_WIDTH - 300) // 2 + 270 * volume_level, SCREEN_HEIGHT // 2 - 60, 30, 20)
        pygame.draw.rect(screen, (100, 100, 100), slider_rect)
        pygame.draw.rect(screen, (0, 255, 0), slider_button_rect)

        volume_percentage = f"{int(volume_level * 101)}%"
        draw_text(volume_percentage, font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10)

        draw_text('Volume', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90)

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
                    volume_level = (mx - slider_rect.x) / slider_rect.width
                    pygame.mixer.music.set_volume(volume_level)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint((mx, my)):
                        current_text = (current_text + 1) % len(text_options)
                        if current_text == 0:
                            player.control = 0
                        else:
                            player.control = 1
                    if button_2.collidepoint((mx, my)):
                        setting_running = False

        pygame.display.update()
        clock.tick(60)

def upgrade_UI():
    global BULLET_SPEED, max_lives, damage_level, bullet_speed_level, live_level, damage_level_need_coin, bullet_speed_level_need_coin, live_level_need_coin
    upgrade_UI_running = True

    background = pygame.image.load(f'img/background/upgrade_background.jpg')
    background_bottom = background
    background_rect = background.get_rect()
    background_rect_bottom = background_bottom.get_rect()
    background_rect_bottom.top = background_rect.bottom

    while upgrade_UI_running:
        background_rect.move_ip(0, 2)
        background_rect_bottom.move_ip(0, 2)
        if background_rect.top >= SCREEN_HEIGHT:
            background_rect.bottom = background_rect_bottom.top
        if background_rect_bottom.top >= SCREEN_HEIGHT:
            background_rect_bottom.bottom = background_rect.top

        screen.blit(background, background_rect)
        screen.blit(background_bottom, background_rect_bottom)

        draw_text('Upgrade Menu', font, (255, 255, 255), screen, SCREEN_WIDTH/2, 150)

        mx, my = pygame.mouse.get_pos()

        button_width = 450
        button_height = 50
        button_1 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 200, button_width, button_height)
        button_2 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 100, button_width, button_height)
        button_3 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2, button_width, button_height)
        button_4 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 100, button_width, button_height)

        pygame.draw.rect(screen, (0, 200, 0), button_1)
        pygame.draw.rect(screen, (0, 0, 200), button_2)
        pygame.draw.rect(screen, (200, 0, 200), button_3)
        pygame.draw.rect(screen, (200, 0, 0), button_4)

        coin_text = font.render('Coin: {}'.format(player.coin), True, (255, 185, 0))
        screen.blit(coin_text, (10, 100)) 
        
        draw_text(f'Lv.{damage_level} Add bullet damage', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200)
        draw_text(f'Lv.{bullet_speed_level} Add bullet speed', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        draw_text(f'Lv.{live_level} Add Live', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text('Back main menu', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)

        draw_text(f'Cost: {damage_level_need_coin} coins', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200 + button_height + 5)
        draw_text(f'Cost: {bullet_speed_level_need_coin} coins', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100 + button_height + 5)
        draw_text(f'Cost: {live_level_need_coin} coins', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + button_height + 5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint((mx, my)):
                        if player.coin >= damage_level_need_coin:
                            player.coin -= damage_level_need_coin
                            player.damage += 1
                            damage_level += 1
                            damage_level_need_coin = damage_level * 1234
                    if button_2.collidepoint((mx, my)):
                        if player.coin >= bullet_speed_level_need_coin:
                            player.coin -= bullet_speed_level_need_coin
                            BULLET_SPEED += 1
                            bullet_speed_level += 1
                            bullet_speed_level_need_coin = bullet_speed_level * 321
                            print("Bullet's speed is ", BULLET_SPEED, " now")
                    if button_3.collidepoint((mx, my)):
                        if player.coin >= live_level_need_coin:
                            player.coin -= live_level_need_coin
                            max_lives += 1
                            live_level += 1
                            live_level_need_coin = live_level * 5432
                            print("max_lives is ", max_lives, " now")
                    if button_4.collidepoint((mx, my)):
                        upgrade_UI_running = False

        pygame.display.update()
        clock.tick(60)

def credits():
    credits_running = True
    while credits_running:
        screen.fill((0,0,0))
        draw_text('Credits', font, (255, 255, 255), screen, SCREEN_WIDTH/2, 150)

        mx, my = pygame.mouse.get_pos()

        button_width = 200
        button_height = 50
        button_1 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 350, button_width, button_height)

        pygame.draw.rect(screen, (200, 0, 0), button_1)
        
        draw_text('Programmer', font, (90, 90, 225), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 240)
        draw_text('LukeTseng', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200)

        draw_text('Game Designer', font, (90, 90, 225), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140)
        draw_text('LukeTseng', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)

        draw_text('Graph Artist (Material Usage)', font, (90, 90, 225), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
        draw_text('FoozleCC', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        draw_text('Background (Material Usage)', font, (90, 90, 225), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        draw_text('Leonardo AI', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)

        draw_text('Music (Material Usage)', font, (90, 90, 225), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160)
        draw_text('OpenGameArt : Oblidivm', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200)

        draw_text('Game Engine : Pygame', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 280)

        draw_text('Back', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 350)

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
    while chose_level_running:
        screen.fill((0, 0, 0))
        for i in range(1, 16):
            if i <= level:
                button_color = (0, 200, 0)  # Green for current level
            else:
                button_color = (200, 0, 0)  # Red for locked levels
            button = pygame.Rect((SCREEN_WIDTH - 200) // 2, 50 * i, 200, 40)
            pygame.draw.rect(screen, button_color, button)
            draw_text(f'Level {i}', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, 50 * i + 20)

        button_back = pygame.Rect((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 100, 200, 40)
        pygame.draw.rect(screen, (100, 100, 100), button_back)
        draw_text('Back', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i in range(1, 16):
                    button = pygame.Rect((SCREEN_WIDTH - 200) // 2, 50 * i, 200, 40)
                    if button.collidepoint((mx, my)):
                        if i <= level:
                            play_music("music/battle_in_the_stars.ogg")
                            level = i
                            chose_level_running = False
                            player.out_of_game = False
                            reset_continue_game()
                            break
                if button_back.collidepoint((mx, my)):
                    chose_level_running = False
                    main_menu()
        pygame.display.update()
        clock.tick(60)

def chose_hard_level():
    global hard_level
    chose_hard_level_running = True
    while chose_hard_level_running:
        screen.fill((0, 0, 0))
        button_back = pygame.Rect((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 100, 200, 40)
        pygame.draw.rect(screen, (100, 100, 100), button_back)
        draw_text('Back', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        if is_complete_game:
            for i in range(1, 16):
                if i <= hard_level:
                    button_color = (0, 200, 0)  # Green for current level
                else:
                    button_color = (200, 0, 0)  # Red for locked levels
                button = pygame.Rect((SCREEN_WIDTH - 200) // 2, 50 * i, 200, 40)
                pygame.draw.rect(screen, button_color, button)
                draw_text(f'Level {i}', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, 50 * i + 20)
        else:
            draw_text("You still haven't completed", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            draw_text("the normal level yet.", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i in range(1, 16):
                    button = pygame.Rect((SCREEN_WIDTH - 200) // 2, 50 * i, 200, 40)
                    if button.collidepoint((mx, my)):
                        if i <= hard_level:
                            hard_level = i
                            chose_hard_level_running = False
                            player.out_of_game = False
                            reset_continue_game()
                            break
                if button_back.collidepoint((mx, my)):
                    chose_hard_level_running = False
                    main_menu()
        pygame.display.update()
        clock.tick(60)

def main_menu():
    play_music("music/brave_pilots_menu_screen.ogg")
    main_running = True
    button_width = 200
    button_height = 50
    button_texts = ['Play', 'Upgrade', 'Setting', 'Exit', 'Credits', 'Hard Mode']
    button_colors = [(0, 200, 0), (200, 0, 200), (0, 200, 200), (200, 0, 0), (200, 200, 0), (255, 0, 0)]
    button_actions = [chose_level, upgrade_UI, setting, sys.exit, credits, chose_hard_level]
    buttons = [pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 240 + i * 120, button_width, button_height) for i in range(len(button_texts))]

    background = pygame.image.load(f'img/background/menu_background.jpg')
    background_bottom = background
    background_rect = background.get_rect()
    background_rect_bottom = background_bottom.get_rect()
    background_rect_bottom.top = background_rect.bottom

    while main_running:
        background_rect.move_ip(0, 2)
        background_rect_bottom.move_ip(0, 2)
        if background_rect.top >= SCREEN_HEIGHT:
            background_rect.bottom = background_rect_bottom.top
        if background_rect_bottom.top >= SCREEN_HEIGHT:
            background_rect_bottom.bottom = background_rect.top

        screen.blit(background, background_rect)
        screen.blit(background_bottom, background_rect_bottom)
        draw_text('Main Menu', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, 100)

        mx, my = pygame.mouse.get_pos()
        for idx, button in enumerate(buttons):
            pygame.draw.rect(screen, button_colors[idx], button)
            draw_text(button_texts[idx], font, (255, 255, 255), screen, SCREEN_WIDTH // 2, button.y + 20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for idx, button in enumerate(buttons):
                        if button.collidepoint((mx, my)):
                            if idx == 0 or idx == 5:
                                main_running = False
                            button_actions[idx]()

        pygame.display.update()
        clock.tick(60)

def game_over_screen():
    play_music('music/defeated_game_over_tune.ogg')
    game_over_running = True
    player.out_of_game = True
    pygame.mouse.set_visible(True)
    while game_over_running:
        screen.fill((0, 0, 0))
        draw_text('Game Over', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100)
        draw_text('press 1. return main menu', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text('press 2. exit game', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
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

def all_levels_completed_screen():
    play_music('music/victory_tune.ogg')
    all_levels_completed_running = True
    player.out_of_game = True
    pygame.mouse.set_visible(True)
    while all_levels_completed_running:
        screen.fill((0, 0, 0))
        draw_text('Congratulations!', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100)
        draw_text('All levels completed!', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text('You are unlock the hard mode now.', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
        draw_text('Press 1 to return to main menu', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type is pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    main_menu()
                    all_levels_completed_running = False

def pause_menu():
    pause_running = True
    while pause_running:
        screen.fill((0,0,0))
        draw_text('Pause', font, (255, 255, 255), screen, SCREEN_WIDTH/2, 150)

        mx, my = pygame.mouse.get_pos()

        button_width = 200
        button_height = 50
        button_1 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 180, button_width, button_height)
        button_2 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 60, button_width, button_height)
        button_3 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 60, button_width, button_height)

        pygame.draw.rect(screen, (0, 200, 0), button_1)
        pygame.draw.rect(screen, (200, 0, 200), button_2)
        pygame.draw.rect(screen, (200, 0, 0), button_3)
        
        draw_text('Continue', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180)
        draw_text('Setting', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        draw_text('Back menu', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)

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
    global BOSS_1_GENERATION_ONCE, BOSS_2_GENERATION_ONCE
    BOSS_1_GENERATION_ONCE = False
    BOSS_2_GENERATION_ONCE = False
    stage_clear_running = True
    animation_score = 0
    animation_time = 0
    player.out_of_game = True
    pygame.mouse.set_visible(True)
    while stage_clear_running:
        screen.fill((0, 0, 0))
        draw_text('Stage Clear !', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100)
        draw_text(f'Score: {animation_score}', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        if pygame.time.get_ticks() - animation_time > 5:
            if animation_score <= score:
                animation_score += 1
                animation_time = pygame.time.get_ticks()
        
        button_next_level = pygame.Rect((SCREEN_WIDTH - 200) // 2 - 28, SCREEN_HEIGHT // 2 + 50, 250, 50)
        button_back_menu = pygame.Rect((SCREEN_WIDTH - 200) // 2 - 28, SCREEN_HEIGHT // 2 + 260, 250, 50)
        button_restart_level = pygame.Rect((SCREEN_WIDTH - 200) // 2 - 28, SCREEN_HEIGHT // 2 + 120, 250, 50)
        pygame.draw.rect(screen, (0, 200, 0), button_next_level)
        pygame.draw.rect(screen, (200, 0, 0), button_back_menu)
        pygame.draw.rect(screen, (100, 100, 100), button_restart_level)
        draw_text('Next Level', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT // 2 + 75)
        draw_text('Back Menu', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT // 2 + 285)
        draw_text('Restart Level', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT // 2 + 145)
        
        if level > 1:
            button_previous_level = pygame.Rect((SCREEN_WIDTH - 200 - 55) // 2, SCREEN_HEIGHT // 2 + 190, 250, 50)
            pygame.draw.rect(screen, (0, 0, 200), button_previous_level)
            draw_text('Previous Level', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT // 2 + 215)
        
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
            bullet.kill()
            if not enemy.invincible:
                enemy.hp -= player.damage
                if enemy.hp <= 0:
                    boom_sound_effect.play()
                    player.coin += gain_coin
                    enemies.remove(enemy)
                    explosion = Explosion(enemy.rect.center)
                    all_sprites.add(explosion)
                    score += score_increment
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
        if current_time - last_spawn_time >= 50 and random.random() < ENEMY_GENERATION_THRESHOLDS[enemy_type]:
            enemy = enemy_class(enemies) if Is_support else enemy_class()
            enemies_p[enemy_type].add(enemy)
            all_sprites.add(enemy)
            if not Is_support:
                enemies.add(enemy)
            last_spawn_time = current_time

def draw_health_bar(boss, screen):
    max_health = boss.maxhp
    current_health = boss.hp
    health_bar_length = 100  # Total length of the health bar
    current_health_length = (current_health / max_health) * health_bar_length
    health_bar_height = 10  # Height of the health bar
    # Adjust health bar position based on boss direction
    if boss.direction == 0:  # Right
        health_bar_x = boss.rect.right - health_bar_length
        health_bar_y = boss.rect.top - health_bar_height - 10
    elif boss.direction == 1:  # Down
        health_bar_x = boss.rect.left
        health_bar_y = boss.rect.bottom + 10
    elif boss.direction == 2:  # Left
        health_bar_x = boss.rect.left
        health_bar_y = boss.rect.top - health_bar_height - 10
    elif boss.direction == 3:  # Up
        health_bar_x = boss.rect.left
        health_bar_y = boss.rect.top - health_bar_height - 20
    pygame.draw.rect(screen, (255,0,0), (health_bar_x, health_bar_y, health_bar_length, health_bar_height))
    pygame.draw.rect(screen, (0,255,0), (health_bar_x, health_bar_y, current_health_length, health_bar_height))

def display_text(text, value, color, position):
    rendered_text = font.render('{}: {}'.format(text, value), True, color)
    screen.blit(rendered_text, position)

def display_text_word_by_word(text, position, delay=70):
    rendered_text = ''
    text_sound_effect.play()
    for word in text:
        screen.fill((0, 0, 0)) 
        rendered_text += word
        text_surface = font.render(rendered_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect.topleft)
        pygame.display.update()
        pygame.time.wait(delay)

def display_opening_screen(texts, delay=500):
    pygame.mixer.music.load('music/skyfire_title_screen.ogg')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.3)
    for text in texts:
        screen.fill((0, 0, 0))
        display_text_word_by_word(text, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        text_sound_effect.stop()
        pygame.time.wait(delay)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    text_sound_effect.stop()
    
    text = "Made by LukeTseng"
    font_color = (255, 255, 255)
    text_surface = font.render(text, True, font_color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    for alpha in range(0, 256, 10):
        text_surface.set_alpha(alpha)
        screen.fill((0, 0, 0))
        screen.blit(text_surface, text_rect)
        pygame.display.update()
        pygame.time.wait(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    pygame.time.wait(3000)
    
    for alpha in range(255, -1, -10):
        text_surface.set_alpha(alpha)
        screen.fill((0, 0, 0))
        screen.blit(text_surface, text_rect)
        pygame.display.update()
        pygame.time.wait(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    pygame.time.wait(1000)

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

display_opening_screen(texts)

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
    
    if pygame.time.get_ticks() - level_start_time > 3000:
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

    background_rect.move_ip(0, 1)
    background_rect_bottom.move_ip(0, 1) 

    if background_rect.top >= SCREEN_HEIGHT:
        background_rect.bottom = background_rect_bottom.top
    if background_rect_bottom.top >= SCREEN_HEIGHT:
        background_rect_bottom.bottom = background_rect.top

    screen.blit(background, background_rect)
    screen.blit(background_bottom, background_rect_bottom)

    for boss in enemies_p['enemies_18']:
        draw_health_bar(boss, screen)

    for boss in enemies_p['enemies_11']:
        draw_health_bar(boss, screen)

    for boss in enemies_p['enemies_5']:
        max_health = boss.maxhp
        current_health = boss.hp
        health_bar_length = 100  # Total length of the health bar
        current_health_length = (current_health / max_health) * health_bar_length
        health_bar_height = 10  # Height of the health bar
        pygame.draw.rect(screen, (255,0,0), (boss.rect.x, boss.rect.bottom + 10, health_bar_length, health_bar_height))
        pygame.draw.rect(screen, (0,255,0), (boss.rect.x, boss.rect.bottom + 10, current_health_length, health_bar_height))

    for group in items.values():
        for item in group:
            screen.blit(item.surf, item.rect)

    for enemy_bullet in enemy_bullets:
        screen.blit(enemy_bullet.surf, enemy_bullet.rect)
    
    check_bullet_hit(bullets, enemies_p['enemies_1'], 2, 0.03, 0.01, Explosion_1, 10)
    check_bullet_hit(bullets, enemies_p['enemies_2'], 3, 0.03, 0.01, Explosion_2, 20)
    check_bullet_hit(bullets, enemies_p['enemies_3'], 4, 0.03, 0.01, Explosion_3, 30)
    check_bullet_hit(bullets, enemies_p['enemies_4'], 5, 0.03, 0.01, Explosion_4, 40)
    check_bullet_hit(bullets, enemies_p['enemies_5'], 200, 0.03, 0.01, Explosion_5, 10000)
    check_bullet_hit(bullets, enemies_p['enemies_6'], 6, 0.03, 0.01, Explosion_6, 50)
    check_bullet_hit(bullets, enemies_p['enemies_7'], 7, 0.03, 0.01, Explosion_7, 60)
    check_bullet_hit(bullets, enemies_p['enemies_8'], 8, 0.03, 0.01, Explosion_8, 70)
    check_bullet_hit(bullets, enemies_p['enemies_9'], 9, 0.03, 0.01, Explosion_9, 80)
    check_bullet_hit(bullets, enemies_p['enemies_10'], 10, 0.03, 0.01, Explosion_10, 90)
    check_bullet_hit(bullets, enemies_p['enemies_11'], 600, 0.03, 0.01, Explosion_11, 50000)
    check_bullet_hit(bullets, enemies_p['enemies_12'], 11, 0.03, 0.01, Explosion_12, 100)
    check_bullet_hit(bullets, enemies_p['enemies_13'], 12, 0.03, 0.01, Explosion_13, 110)
    check_bullet_hit(bullets, enemies_p['enemies_14'], 13, 0.03, 0.01, Explosion_14, 120)
    check_bullet_hit(bullets, enemies_p['enemies_15'], 14, 0.03, 0.01, Explosion_15, 130)
    check_bullet_hit(bullets, enemies_p['enemies_16'], 15, 0.03, 0.01, Explosion_16, 140)
    check_bullet_hit(bullets, enemies_p['enemies_17'], 16, 0.03, 0.01, Explosion_17, 150)
    check_bullet_hit(bullets, enemies_p['enemies_18'], 1000, 0.03, 0.01, Explosion_18, 100000)

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

    if player.invincible and pygame.time.get_ticks() - player.last_hit_time > 3000:
        player.invincible = False

    if player.invincible_shield and pygame.time.get_ticks() - player.shield_start_time > 5000:
        player.invincible_shield = False

    if player.lives <= 0:
        game_over_screen()
    
    if level > 15:
        all_levels_completed_screen()
        is_complete_game = True
    
    if score > 100 + (level * 10) * 9: # 100 + (level * 10) * 9
        action = stage_clear_screen(level, score)
        if action == 'next':
            reset_enemies()
            level += 1
            score = 0
            player.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-30)
            player.lives = max_lives
            level_start_time = pygame.time.get_ticks()
        elif action == 'menu':
            main_menu()
        elif action == 'previous':
            reset_enemies()
            level -= 1
            score = 0
            player.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-30)
            player.lives = max_lives
            level_start_time = pygame.time.get_ticks() 
        elif action == 'restart':
            reset_enemies()
            score = 0
            player.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-30)
            player.lives = max_lives
            level_start_time = pygame.time.get_ticks() 

    if level <= len(backgrounds): 
        background = backgrounds[level - 1]
        background_bottom = backgrounds[level - 1]

    for entity in all_sprites:
        if entity == player:
            player.draw(screen)
        else:
            screen.blit(entity.surf, entity.rect)

    for entity in all_sprites:
        if isinstance(entity, Enemy) and entity.invincible:
            if entity.shield_surf is not None:
                screen.blit(entity.shield_surf, entity.shield_rect)

    display_text('Level', level, (255, 255, 255), (10, 10))
    display_text('Score', score, (255, 255, 255), (10, 40))
    display_text('Live', player.lives, (0, 235, 0), (10, 70))
    display_text('Coin', player.coin, (255, 185, 0), (10, 100))

    pygame.display.flip()
    clock.tick(180) 

pygame.quit()
sys.exit()