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
bullet_speed_level = 0
live_level = 0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_icon(pygame.image.load('icon.png'))
pygame.display.set_caption('Space Shooter - Pygame Edition v1.0 - By: @LukeTseng')
font = pygame.font.Font('font.ttf', 36)
clock = pygame.time.Clock()

level = 1
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
    player.lives = 5
    global score, level
    score, level = 0, 1

current_text = 0 
def setting():
    global current_text
    setting_running = True
    text_options = ['Control the sprite with keyboard', 'Control the sprite with cursor']

    while setting_running:
        screen.fill((0,0,0))
        draw_text('Setting', font, (255, 255, 255), screen, SCREEN_WIDTH/2, 150)

        mx, my = pygame.mouse.get_pos()

        button_width = 200
        button_height = 50
        button_1 = pygame.Rect((SCREEN_WIDTH - 550) // 2, (SCREEN_HEIGHT - button_height) // 2 - 180, 550, button_height)
        button_2 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 60, button_width, button_height)
        
        pygame.draw.rect(screen, (0, 200, 0), button_1)
        pygame.draw.rect(screen, (200, 0, 0), button_2)

        text = text_options[current_text]
        draw_text(text , font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180)
        draw_text('Back menu', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
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

def main_menu():
    main_running = True
    while main_running:
        screen.fill((0,0,0))
        draw_text('Main Menu', font, (255, 255, 255), screen, SCREEN_WIDTH/2, 150)

        mx, my = pygame.mouse.get_pos()

        button_width = 200
        button_height = 50
        button_1 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 180, button_width, button_height)
        button_2 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 60, button_width, button_height)
        button_3 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 60, button_width, button_height)
        button_4 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 180, button_width, button_height)

        pygame.draw.rect(screen, (0, 200, 0), button_1)
        pygame.draw.rect(screen, (0, 0, 200), button_2)
        pygame.draw.rect(screen, (200, 0, 200), button_3)
        pygame.draw.rect(screen, (200, 0, 0), button_4)
        
        draw_text('Play', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180)
        draw_text('Upgrade', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        draw_text('Setting', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        draw_text('Exit', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint((mx, my)):
                        main_running = False
                        player.out_of_game = False
                        break
                    if button_2.collidepoint((mx, my)):
                        upgrade_UI()
                    if button_3.collidepoint((mx, my)):
                        setting()
                    if button_4.collidepoint((mx, my)):
                        pygame.quit()
                        sys.exit()

        pygame.display.update()
        clock.tick(60)

def upgrade_UI():
    global BULLET_SPEED, max_lives, damage_level, bullet_speed_level, live_level
    upgrade_UI_running = True
    while upgrade_UI_running:
        screen.fill((0,0,0))
        draw_text('Upgrade Menu', font, (255, 255, 255), screen, SCREEN_WIDTH/2, 150)

        mx, my = pygame.mouse.get_pos()

        button_width = 450
        button_height = 50
        button_1 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 180, button_width, button_height)
        button_2 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 60, button_width, button_height)
        button_3 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 60, button_width, button_height)
        button_4 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 180, button_width, button_height)

        pygame.draw.rect(screen, (0, 200, 0), button_1)
        pygame.draw.rect(screen, (0, 0, 200), button_2)
        pygame.draw.rect(screen, (200, 0, 200), button_3)
        pygame.draw.rect(screen, (200, 0, 0), button_4)

        coin_text = font.render('Coin: {}'.format(player.coin), True, (255, 185, 0))
        screen.blit(coin_text, (10, 100)) 
        
        draw_text(f'Lv.{damage_level} Add bullet damage', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180)
        draw_text(f'Lv.{bullet_speed_level} Add bullet speed', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        draw_text(f'Lv.{live_level} Add Live', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        draw_text('Back main menu', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint((mx, my)):
                        player.damage += 1
                        damage_level += 1
                    if button_2.collidepoint((mx, my)):
                        BULLET_SPEED += 1
                        bullet_speed_level += 1
                        print("Bullet's speed is ", BULLET_SPEED, " now")
                    if button_3.collidepoint((mx, my)):
                        max_lives += 1
                        live_level += 1
                        print("max_lives is ", max_lives, " now")
                    if button_4.collidepoint((mx, my)):
                        upgrade_UI_running = False

        pygame.display.update()
        clock.tick(60)

def game_over_screen():
    game_over_running = True
    player.out_of_game = True
    reset_game()
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
                        reset_game()
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
                    player.out_of_game = False
                    return 'next'
                if button_back_menu.collidepoint((mx, my)):
                    stage_clear_running = False
                    # Return menu
                    return 'menu'
                if level > 1 and button_previous_level.collidepoint((mx, my)):
                    # Return pervious level
                    player.out_of_game = False
                    return 'previous'
                if button_restart_level.collidepoint((mx, my)):
                    # Restart current level
                    player.out_of_game = False
                    return 'restart'

def check_bullet_hit(bullets, enemies, score_increment, drop_rate_1, drop_rate_2, Explosion):
    global score
    for bullet in bullets:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hit_enemies:
            bullet.kill()
            if not enemy.invincible:
                enemy.hp -= player.damage
                if enemy.hp <= 0:
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

def generate_enemy(level, enemy_type, enemy_class, boss=False, Is_support=False):
    if boss:
        if not BOSS_GENERATION_ONCE[enemy_type]:
            boss = enemy_class()
            enemies_p[enemy_type].add(boss)
            all_sprites.add(boss)
            BOSS_GENERATION_ONCE[enemy_type] = True
    else:
        if not(Is_support):
            if random.random() < ENEMY_GENERATION_THRESHOLDS[enemy_type]:
                enemy = enemy_class()
                enemies_p[enemy_type].add(enemy)
                all_sprites.add(enemy)
                enemies.add(enemy)
        else:
            if random.random() < ENEMY_GENERATION_THRESHOLDS[enemy_type]:
                enemy = enemy_class(enemies)
                enemies_p[enemy_type].add(enemy)
                all_sprites.add(enemy)

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
            if level > 6:
                generate_enemy(level, 'enemies_7', Enemy_6)
            if level > 7:
                generate_enemy(level, 'enemies_8', Enemy_7)
            if level > 8:
                generate_enemy(level, 'enemies_9', Enemy_8, Is_support=True)
                generate_enemy(level, 'enemies_10', Enemy_9)
            if level == 10:
                generate_enemy(level, 'enemies_11', Boss_2, boss=True)
        elif level > 10:
            generate_enemy(level, 'enemies_12', Enemy_10)
            generate_enemy(level, 'enemies_13', Enemy_11)
            if level > 11:
                generate_enemy(level, 'enemies_14', Enemy_12)
            if level > 12:
                generate_enemy(level, 'enemies_15', Enemy_13)
            if level > 13:
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
    
    check_bullet_hit(bullets, enemies_p['enemies_1'], 1, 0.3, 0.05, Explosion_1)
    check_bullet_hit(bullets, enemies_p['enemies_2'], 3, 0.06, 0.09, Explosion_2)
    check_bullet_hit(bullets, enemies_p['enemies_3'], 5, 0.09, 0.1, Explosion_3)
    check_bullet_hit(bullets, enemies_p['enemies_4'], 2, 0.02, 0.15, Explosion_4)
    check_bullet_hit(bullets, enemies_p['enemies_5'], 100, 0.3, 0.5, Explosion_5)
    check_bullet_hit(bullets, enemies_p['enemies_6'], 2, 0.1, 0.1, Explosion_6)
    check_bullet_hit(bullets, enemies_p['enemies_7'], 4, 0.15, 0.1, Explosion_7)
    check_bullet_hit(bullets, enemies_p['enemies_8'], 6, 0.15, 0.1, Explosion_8)
    check_bullet_hit(bullets, enemies_p['enemies_9'], 3, 0.15, 0.1, Explosion_9)
    check_bullet_hit(bullets, enemies_p['enemies_10'], 10, 0.3, 0.3, Explosion_10)
    check_bullet_hit(bullets, enemies_p['enemies_11'], 400, 0.5, 0.5, Explosion_11)
    check_bullet_hit(bullets, enemies_p['enemies_12'], 3, 0.15, 0.1, Explosion_12)
    check_bullet_hit(bullets, enemies_p['enemies_13'], 5, 0.15, 0.1, Explosion_13)
    check_bullet_hit(bullets, enemies_p['enemies_14'], 7, 0.2, 0.1, Explosion_14)
    check_bullet_hit(bullets, enemies_p['enemies_15'], 9, 0.25, 0.25, Explosion_15)
    check_bullet_hit(bullets, enemies_p['enemies_16'], 11, 0.25, 0.25, Explosion_16)
    check_bullet_hit(bullets, enemies_p['enemies_17'], 13, 0.35, 0.35, Explosion_17)
    check_bullet_hit(bullets, enemies_p['enemies_18'], 600, 0.6, 0.6, Explosion_18)

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

    if player.lives <= 0 or level > 20:
        game_over_screen()
    
    if score > 75 + (level * 10) * 5: # 75 + (level * 10) * 5
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

    level_text = font.render('Level: {}'.format(level), True, (255, 255, 255))
    screen.blit(level_text, (10, 10)) 

    score_text = font.render('Score: {}'.format(score), True, (255, 255, 255))
    screen.blit(score_text, (10, 40))

    lives_text = font.render('Live: {}'.format(player.lives), True, (0, 235, 0))
    screen.blit(lives_text, (10, 70)) 

    coin_text = font.render('Coin: {}'.format(player.coin), True, (255, 185, 0))
    screen.blit(coin_text, (10, 100)) 

    pygame.display.flip()
    clock.tick(180) 

pygame.quit()
sys.exit()