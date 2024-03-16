import pygame
import sys
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 600, 900
PLAYER_SPEED = 4
BULLET_SPEED = 20
ENEMY_GENERATION_THRESHOLDS = {
    'ENEMY_1': 0.02,
    'ENEMY_2': 0.007,
    'ENEMY_3': 0.0085,
    'ENEMY_4': 0.003,
    'ENEMY_5': 0.01,
    'ENEMY_6': 0.007,
    'ENEMY_7': 0.0085,
    'ENEMY_8': 0.003,
    'ENEMY_9': 0.001,
}

BOSS_GENERATION_ONCE = False

level_start_time = 0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font('font.ttf', 36)
clock = pygame.time.Clock()

max_lives = 5
player_bullet_angle = [10, 0, -10]

level = 6
backgrounds = [pygame.image.load(f'img/background/lv{i}_background.jpg') for i in range(1, 21)]
background = backgrounds[0]
background_bottom = backgrounds[0]
background_rect = background.get_rect()
background_rect_bottom = background_bottom.get_rect()
background_rect_bottom.top = background_rect.bottom

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = {
            'full_health': pygame.image.load('img/player/main_ship/full_health.png').convert_alpha(),
            'slight_damaged': pygame.image.load('img/player/main_ship/slight_damaged.png').convert_alpha(),
            'damaged': pygame.image.load('img/player/main_ship/damaged.png').convert_alpha(),
            'very_damaged': pygame.image.load('img/player/main_ship/very_damaged.png').convert_alpha(),
        }
        self.images_invincible = {
            'full_health': pygame.Surface((self.images['full_health'].get_width(), self.images['full_health'].get_height()), pygame.SRCALPHA),
            'slight_damaged': pygame.Surface((self.images['slight_damaged'].get_width(), self.images['slight_damaged'].get_height()), pygame.SRCALPHA),
            'damaged': pygame.Surface((self.images['damaged'].get_width(), self.images['damaged'].get_height()), pygame.SRCALPHA),
            'very_damaged': pygame.Surface((self.images['very_damaged'].get_width(), self.images['very_damaged'].get_height()), pygame.SRCALPHA),
        }
        for key in self.images:
            self.images_invincible[key].blit(self.images[key], (0, 0))
            self.images_invincible[key].fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
        self.rect = self.images['full_health'].get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-30))
        self.lives = max_lives 
        self.invincible = False 
        self.last_hit_time = 0 
        self.image_key = 'full_health'
        self.index = 0 
        self.last_shot_time = pygame.time.get_ticks()
        self.shield_start_time = pygame.time.get_ticks()
        self.shield_image_time = pygame.time.get_ticks()
        self.shield_images = [pygame.image.load(f'img/player/shields/round_shield/round_shield_frame_{i}.png').convert_alpha() for i in range(1,13)]
        self.shield_index = 0
        self.shield_surf = None
        self.shield_rect = None
        self.invincible_shield = False

    def activate_shield(self):
        self.invincible_shield = True
        self.shield_start_time = pygame.time.get_ticks()

    def update(self, pressed_keys, mouse_pos):
        if control == 0:
            if pressed_keys[pygame.K_UP]:
                self.rect.move_ip(0, -PLAYER_SPEED)
            if pressed_keys[pygame.K_DOWN]:
                self.rect.move_ip(0, PLAYER_SPEED)
            if pressed_keys[pygame.K_LEFT]:
                self.rect.move_ip(-PLAYER_SPEED, 0)
            if pressed_keys[pygame.K_RIGHT]:
                self.rect.move_ip(PLAYER_SPEED, 0)
        else:
            self.rect.center = mouse_pos

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        
        if pygame.time.get_ticks() - self.last_shot_time > 15: 
            for angle in player_bullet_angle:
                bullet = Bullet(self)
                bullet.velocity = pygame.math.Vector2(0, -BULLET_SPEED).rotate(angle) 
                bullets.add(bullet)
                all_sprites.add(bullet)
                self.last_shot_time = pygame.time.get_ticks()
    
    def draw(self, screen):
        if self.lives == 5:
            self.image_key = 'full_health'
        elif self.lives == 4:
            self.image_key = 'slight_damaged'
        elif self.lives == 3:
            self.image_key = 'damaged'
        elif self.lives == 1:
            self.image_key = 'very_damaged'

        if self.invincible and pygame.time.get_ticks() // 250 % 2 == 0:
            image = self.images_invincible[self.image_key]
        else:
            image = self.images[self.image_key]

        if self.invincible_shield:
            if pygame.time.get_ticks() - self.shield_image_time > 100: 
                self.shield_index = (self.shield_index + 1) % len(self.shield_images)
                self.shield_surf = self.shield_images[self.shield_index]
                self.shield_image_time = pygame.time.get_ticks()
            self.shield_rect = self.shield_surf.get_rect(center = (player.rect.centerx, player.rect.centery))
            screen.blit(player.shield_surf, player.shield_rect)

        screen.blit(image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.images = [pygame.transform.scale(pygame.image.load(f'img/player/bullets/zapper_assets/zapper_frame_{i}.png'), (6, 32)).convert_alpha() for i in range(1, 9)]
        self.velocity = pygame.math.Vector2(0, BULLET_SPEED) 
        self.index = 0 
        self.surf = self.images[self.index] 
        self.rect = self.surf.get_rect(center = (player.rect.centerx, player.rect.top))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

    def update(self, pressed_keys=None, mouse_pos=None):
        
        if self.rect.bottom < 0:
            self.kill()
        self.index = (self.index + 1) % len(self.images) 
        self.surf = self.images[self.index] 

        self.pos_y += self.velocity.y
        self.pos_x += self.velocity.x 
        self.rect.y = int(self.pos_y)
        self.rect.x = int(self.pos_x) 

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, enemy, image_path, image_scale, image_range):
        super().__init__()
        if image_scale != None:
            self.images = [pygame.transform.scale(pygame.image.load(f'{image_path}{i}.png'), image_scale).convert_alpha() for i in range(1, image_range)]
        else:
            self.images = [pygame.image.load(f'{image_path}{i}.png').convert_alpha() for i in range(1, image_range)]
        self.index = 0
        self.surf = self.images[self.index]
        self.rect = self.surf.get_rect(center = (enemy.rect.centerx, enemy.rect.bottom))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.last_update = pygame.time.get_ticks()

    def update(self, pressed_keys=None, mouse_pos=None):
        if pygame.time.get_ticks() - self.last_update > 100:
            self.index = (self.index + 1) % len(self.images)
            self.surf = self.images[self.index]
            self.last_update = pygame.time.get_ticks()
        self.pos_y += 3
        self.rect.y = int(self.pos_y)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class EnemyBullet_1(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv1_to_5/Projectiles/Bullet_assets/Bullet_frame_', (4, 19), 5)

class EnemyBullet_2(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv1_to_5/Projectiles/Torpedo_assets/Torpedo_frame_', (7.5, 28.5), 4)

class EnemyBullet_3(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv1_to_5/Projectiles/Big_Bullet_assets/Big_Bullet_frame_', (13.5, 20.25), 4)
        self.velocity = pygame.math.Vector2(0, 1) 
        self.last_update = pygame.time.get_ticks()

    def update(self, pressed_keys=None, mouse_pos=None):
        if pygame.time.get_ticks() - self.last_update > 100:  
            self.index = (self.index + 1) % len(self.images)
            self.surf = self.images[self.index]
            self.last_update = pygame.time.get_ticks()
        self.pos_y += self.velocity.y
        self.pos_x += self.velocity.x 
        self.rect.y = int(self.pos_y)
        self.rect.x = int(self.pos_x) 
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class EnemyBullet_4(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv1_to_5/Projectiles/Ray_assets/Ray_frame_', None, 4)

class EnemyBullet_5(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv6_to_10/Projectile/Bolt_assets/Bolt_frame_', None, 7)

class EnemyBullet_6(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv6_to_10/Projectile/Torpedo_assets/Torpedo_frame_', None, 4)

class EnemyBullet_7(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv6_to_10/Projectile/Ray_assets/Ray_frame_', None, 5)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_path, shield_image_path, shield_scale=None, scale=None, speed=1, hp=100, shield_frames=14):
        super().__init__()
        original_image = pygame.image.load(image_path).convert_alpha()
        self.mask = pygame.mask.from_surface(original_image)
        self.surf = pygame.transform.scale(original_image, scale) if scale else original_image
        self.rect = self.surf.get_rect(center = (random.randint(15, SCREEN_WIDTH-15), 0))
        self.shield_index = 0 
        if shield_image_path:
            original_image = pygame.image.load(f'{shield_image_path}1.png').convert_alpha()
            original_size = original_image.get_size()
            self.shield_images = [pygame.transform.scale(pygame.image.load(f'{shield_image_path}{i}.png').convert_alpha(), shield_scale if shield_scale else original_size) for i in range(1, shield_frames)]
            self.shield_surf = self.shield_images[self.shield_index] 
            self.shield_rect = self.shield_surf.get_rect(center=self.rect.center) 
        else:
            self.shield_images = None
            self.shield_surf = None
            self.shield_rect = None
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.hp = hp
        self.speed = speed 
        self.invincible = False  
        self.last_update = pygame.time.get_ticks()

    def update(self, bullet_class, bullet_probability):
        self.pos_y += self.speed
        self.rect.y = int(self.pos_y)
        if random.random() < bullet_probability:
            bullet = bullet_class(self)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)
        if self.invincible:
            if self.shield_rect is not None:
                self.shield_rect.center = self.rect.center
                if pygame.time.get_ticks() - self.last_update > 75:
                    self.shield_index = (self.shield_index + 1) % len(self.shield_images)
                    self.shield_surf = self.shield_images[self.shield_index]
                    self.last_update = pygame.time.get_ticks()
        if self.rect.top > SCREEN_HEIGHT or self.hp <= 0:
            self.kill()

class Enemy_1(Enemy):
    def __init__(self):
        super().__init__('img/enemy/lv1_to_5/base/Scout_assets/Scout_frame_1.png', 'img/enemy/lv1_to_5/Shield/Scout_assets/Scout_Shield_frame_', (39.4, 42.8), (37.4, 40.8), 2, 100, 14)
    
    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_1, 0.01)

class Enemy_2(Enemy):
    def __init__(self):
        super().__init__('img/enemy/lv1_to_5/base/Torpedo_assets/Torpedo_frame_1.png', 'img/enemy/lv1_to_5/Shield/Torpedo_assets/Torpedo_frame_', None, None, 1, 600, 11)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_2, 0.002)

class Enemy_3(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv1_to_5/base/Frigate_assets/Frigate_frame_1.png', 'img/enemy/lv1_to_5/Shield/Frigate_assets/Frigate_Shield_frame_', None, None, 4, 300, 39)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_2, 0.000001)

class Enemy_4(Enemy):

    targets = [] 

    def __init__(self, enemies):
        super().__init__('img/enemy/lv1_to_5/base/Support_assets/Support_frame_1.png', None, None, None, 2, 200)
        self.target = None
        for enemy in enemies.sprites():
            if self.targets.count(enemy) < 1: 
                self.target = enemy
                self.targets.append(enemy) 
                break
        self.Is_die = False
    
    def remove_target(self):
        if self.target and self.target in self.targets:
            self.targets.remove(self.target)  
            self.target.invincible = False  

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_2, 0.000001)
        if self.target not in enemies or not enemies:
            self.target = None
        if self.target:
            if self.Is_die == False:
                self.target.invincible = True
        if self.target:
            self.rect.centerx = self.target.rect.centerx + self.target.rect.width
            self.rect.centery = self.target.rect.centery
        else:
            self.rect.centery += self.speed
        if self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0 or self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()
            self.remove_target()
        if self.hp <= 0:
            self.kill()
            self.remove_target()

    def __del__(self):
        if self.target in self.targets: 
            self.targets.remove(self.target)  
        if self.target:
            self.target.invincible = False 

class Enemy_5(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv6_to_10/base/Scout_assets/Scout_frame_1.png', 'img/enemy/lv6_to_10/Shield/Scout_assets/Scout_frame__', (36, 33), (36, 33), 2, 500, 19)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_5, 0.008)

class Enemy_6(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv6_to_10/base/Torpedo_assets/Torpedo_frame_1.png', 'img/enemy/lv6_to_10/Shield/Torpedo_assets/Torpedo_frame_', None, None, 1, 1500, 9)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_6, 0.003)

class Enemy_7(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv6_to_10/base/Frigate_assets/Frigate_frame_1.png', 'img/enemy/lv6_to_10/Shield/Frigate_assets/Frigate_frame_', None, None, 4, 1000, 9)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_5, 0.009)

class Enemy_8(Enemy):

    targets = [] 

    def __init__(self, enemies):
        super().__init__('img/enemy/lv6_to_10/base/Support_assets/Support_frame_1.png', None, None, None, 2, 1000)
        self.target = None
        for enemy in enemies.sprites():
            if self.targets.count(enemy) < 1: 
                self.target = enemy
                self.targets.append(enemy) 
                break
        self.Is_die = False
    
    def remove_target(self):
        if self.target and self.target in self.targets:
            self.targets.remove(self.target)  
            self.target.invincible = False  

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_2, 0.000001)
        if self.target not in enemies or not enemies:
            self.target = None
        if self.target:
            if self.Is_die == False:
                self.target.invincible = True
        if self.target:
            self.rect.centerx = self.target.rect.centerx + self.target.rect.width
            self.rect.centery = self.target.rect.centery
        else:
            self.rect.centery += self.speed
        if self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0 or self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()
            self.remove_target()
        if self.hp <= 0:
            self.kill()
            self.remove_target()

    def __del__(self):
        if self.target in self.targets: 
            self.targets.remove(self.target)  
        if self.target:
            self.target.invincible = False 

class Enemy_9(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv6_to_10/base/Battlecruiser_assets/Battlecruiser_frame_1.png', 'img/enemy/lv6_to_10/Shield/Battlecruiser_assets/Battlecruiser_frame_', None, None, 0, 6000, 9)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_7, 0.05)

class Boss_1(Enemy):
    def __init__(self):
        super().__init__('img/enemy/lv1_to_5/base/Battlecruiser_assets/Battlecruiser_frame_1.png', None, None, (108,132), 2, 50000)
        self.show_warning = False
        #self.warning_image = pygame.image.load('.png').convert_alpha()
        self.rect.midtop = (SCREEN_WIDTH / 2, 0) 
        self.attack_timer = pygame.time.get_ticks()
        self.laser_cooldown = 15000  
        self.laser_charging_duration = 2000 
        self.laser_firing_duration = 2000  
        self.laser_charging = False
        self.laser_firing = False
        self.scatter_cooldown = 1000 
        self.laser_firing_start_time = pygame.time.get_ticks()
        self.laser_charging_start_time = pygame.time.get_ticks()
        self.scatter_timer = pygame.time.get_ticks()
        self.speed = 2 
        self.direction = 1  
    
    def update(self, pressed_keys=None, mouse_pos=None):
        self.move_sideways() 
        self.attack()
        if self.hp <= 0:
            self.kill()
    
    def move_sideways(self):
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.direction *= -1
        self.rect.move_ip(self.speed * self.direction, 0)
    
    def attack(self):
        now = pygame.time.get_ticks()
        if now - self.attack_timer >= self.laser_cooldown:
            if not self.laser_charging and not self.laser_firing:
                self.laser_charging = True
                self.laser_charging_start_time = now
            if now - self.laser_charging_start_time >= self.laser_charging_duration:
                self.laser_charging = False
                self.laser_firing = True
                self.laser_firing_start_time = now
            if now - self.laser_firing_start_time >= self.laser_firing_duration:
                self.laser_firing = False
                self.attack_timer = now
                print("fire_laser")
                self.fire_laser()
        
        if now - self.scatter_timer >= self.scatter_cooldown:
            self.scatter_timer = now
            print("fire_scatter_bullets")
            self.fire_scatter_bullets()
    
    def fire_laser(self):
        bullet = EnemyBullet_4(self)
        enemy_bullets.add(bullet)
        all_sprites.add(bullet)
    
    def fire_scatter_bullets(self):
        for angle in [45, 0, -45]:
            bullet = EnemyBullet_3(self)
            bullet.velocity = pygame.math.Vector2(0, 3).rotate(angle)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)
    
    def draw(self, screen):
        super().draw(screen)
        if self.show_warning:
            screen.blit(self.warning_image, (0, 0))
            
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, images):
        super().__init__()
        self.images = images
        self.index = 0 
        self.surf = self.images[self.index] 
        self.rect = self.surf.get_rect(center=center)
        self.last_update = pygame.time.get_ticks()

    def update(self, pressed_keys=None, mouse_pos=None):
        if pygame.time.get_ticks() - self.last_update > 100: 
            self.index = (self.index + 1) % len(self.images) 
            self.surf = self.images[self.index] 
            self.last_update = pygame.time.get_ticks()
            if self.index == 0:
                self.kill()

class Explosion_1(Explosion):
    def __init__(self, center):
        images = []
        for i in range(1, 9):
            image = pygame.image.load(f'img/enemy/lv1_to_5/base/Scout_assets/Scout_frame_{i}.png').convert_alpha()
            if i in [1, 2]: 
                image = pygame.transform.scale(image, (37.4, 40.8))
            images.append(image)
        super().__init__(center, images)

class Explosion_2(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv1_to_5/base/Torpedo_assets/Torpedo_frame_{i}.png').convert_alpha() for i in range(1,9)]
        super().__init__(center, images)

class Explosion_3(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv1_to_5/base/Frigate_assets/Frigate_frame_{i}.png').convert_alpha() for i in range(1,9)]
        super().__init__(center, images)

class Explosion_4(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv1_to_5/base/Support_assets/Support_frame_{i}.png').convert_alpha() for i in range(1,9)]
        super().__init__(center, images)

class Explosion_5(Explosion):
    def __init__(self, center):
        images = []
        for i in range(1, 13):
            image = pygame.image.load(f'img/enemy/lv1_to_5/base/Battlecruiser_assets/Battlecruiser_frame_{i}.png').convert_alpha()
            if i <= 6:  # 只調整前6幀的大小
                image = pygame.transform.scale(image, (108, 132)) 
            images.append(image)
        super().__init__(center, images)

class Explosion_6(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv6_to_10/base/Scout_assets/Scout_frame_{i}.png').convert_alpha() for i in range(1,16)]
        super().__init__(center, images)

class Explosion_7(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv6_to_10/base/Torpedo_assets/Torpedo_frame_{i}.png').convert_alpha() for i in range(1,16)]
        super().__init__(center, images)

class Explosion_8(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv6_to_10/base/Frigate_assets/Frigate_frame_{i}.png').convert_alpha() for i in range(1,16)]
        super().__init__(center, images)

class Explosion_9(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv6_to_10/base/Support_assets/Support_frame_{i}.png').convert_alpha() for i in range(1,16)]
        super().__init__(center, images)

class Explosion_10(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv6_to_10/base/Battlecruiser_assets/Battlecruiser_frame_{i}.png').convert_alpha() for i in range(1,18)]
        super().__init__(center, images)

class BaseItem(pygame.sprite.Sprite):
    def __init__(self, center, image_path, image_scale):
        super().__init__()
        self.images = [pygame.transform.scale(pygame.image.load(f'{image_path}{i}.png').convert_alpha(), image_scale) for i in range(1, 8)]
        self.index = 0 
        self.surf = self.images[self.index] 
        self.rect = self.surf.get_rect(center=center)
        self.pos_y = float(self.rect.y) 
        self.last_animation_time = pygame.time.get_ticks()

    def update(self, pressed_keys=None, mouse_pos=None):
        if pygame.time.get_ticks() - self.last_animation_time > 100:
            self.index = (self.index + 1) % len(self.images) 
            self.surf = self.images[self.index] 
            self.last_animation_time = pygame.time.get_ticks()

        self.pos_y += 2
        self.rect.y = int(self.pos_y) 
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() 

class Item_1(BaseItem):
    def __init__(self, center):
        super().__init__(center, 'img/item/Engines/add_hp/add_hp_frame_', (36 , 25.5))

class Item_2(BaseItem):
    def __init__(self, center):
        super().__init__(center, 'img/item/Shield_Generators/All_around_shield_frame_', (36 , 36))

player = Player()
items = {
    'item_1': pygame.sprite.Group(),
    'item_2': pygame.sprite.Group(),
}
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemies_p = {f"enemies_{i}": pygame.sprite.Group() for i in range(1, 11)}
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

score = 0 
running = True 

control = 0 # control the sprite with cursor or keyboard, keyboard = 0, cursor = 1

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
    global control, current_text
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
                            control = 0
                        else:
                            control = 1
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
    global BULLET_SPEED, max_lives
    upgrade_UI_running = True
    while upgrade_UI_running:
        screen.fill((0,0,0))
        draw_text('Upgrade Menu', font, (255, 255, 255), screen, SCREEN_WIDTH/2, 150)

        mx, my = pygame.mouse.get_pos()

        button_width = 385
        button_height = 50
        button_1 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 180, button_width, button_height)
        button_2 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 - 60, button_width, button_height)
        button_3 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 60, button_width, button_height)
        button_4 = pygame.Rect((SCREEN_WIDTH - button_width) // 2, (SCREEN_HEIGHT - button_height) // 2 + 180, button_width, button_height)

        pygame.draw.rect(screen, (0, 200, 0), button_1)
        pygame.draw.rect(screen, (0, 0, 200), button_2)
        pygame.draw.rect(screen, (200, 0, 200), button_3)
        pygame.draw.rect(screen, (200, 0, 0), button_4)
        
        draw_text('Add bullet', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180)
        draw_text('Making bullet speed up', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        draw_text('Add Live', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        draw_text('Back main menu', font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint((mx, my)):
                        pass
                    if button_2.collidepoint((mx, my)):
                        BULLET_SPEED += 1
                        print("Bullet's speed is ", BULLET_SPEED, " now")
                    if button_3.collidepoint((mx, my)):
                        max_lives += 1
                        print("max_lives is ", max_lives, " now")
                    if button_4.collidepoint((mx, my)):
                        upgrade_UI_running = False

        pygame.display.update()
        clock.tick(60)

def game_over_screen():
    game_over_running = True
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
                    if button_2.collidepoint((mx, my)):
                        setting()
                    if button_3.collidepoint((mx, my)):
                        pause_running = False
                        reset_game()
                        main_menu()

        pygame.display.update()
        clock.tick(60)

def stage_clear_screen(level, score):
    global BOSS_GENERATION_ONCE
    BOSS_GENERATION_ONCE = False
    stage_clear_running = True
    animation_score = 0
    animation_time = 0
    while stage_clear_running:
        screen.fill((0, 0, 0))
        draw_text('Stage Clear !', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100)
        draw_text(f'Score: {animation_score}', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        if pygame.time.get_ticks() - animation_time > 15:
            if animation_score <= score:
                animation_score += 1
                animation_time = pygame.time.get_ticks()
        
        button_next_level = pygame.Rect((SCREEN_WIDTH - 200) // 2 - 28, SCREEN_HEIGHT // 2 + 50, 250, 50)
        button_back_menu = pygame.Rect((SCREEN_WIDTH - 200) // 2 - 28, SCREEN_HEIGHT // 2 + 190, 250, 50)
        pygame.draw.rect(screen, (0, 200, 0), button_next_level)
        pygame.draw.rect(screen, (200, 0, 0), button_back_menu)
        draw_text('Next Level', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT // 2 + 75)
        draw_text('Back Menu', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT // 2 + 215)
        
        if level > 1:
            button_previous_level = pygame.Rect((SCREEN_WIDTH - 200 - 55) // 2, SCREEN_HEIGHT // 2 + 120, 250, 50)
            pygame.draw.rect(screen, (0, 0, 200), button_previous_level)
            draw_text('Previous Level', font, (255, 255, 255), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT // 2 + 145)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if button_next_level.collidepoint((mx, my)):
                    # 進入下一關
                    return 'next'
                if button_back_menu.collidepoint((mx, my)):
                    stage_clear_running = False
                    # 返回主菜單
                    return 'menu'
                if level > 1 and button_previous_level.collidepoint((mx, my)):
                    # 返回上一關
                    return 'previous'

def check_bullet_hit(bullets, enemies, score_increment, drop_rate_1, drop_rate_2, Explosion):
    global score
    for bullet in bullets:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hit_enemies:
            bullet.kill()
            if not enemy.invincible:
                enemy.hp -= 50
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
    for group in [enemies, enemies_p['enemies_1'], enemies_p['enemies_2'], enemies_p['enemies_3'], enemies_p['enemies_4'], enemies_p['enemies_5'], enemies_p['enemies_6'], enemies_p['enemies_7'], enemies_p['enemies_8'], enemies_p['enemies_9'], enemies_p['enemies_10'], enemy_bullets, items['item_1'], items['item_2']]:
        for sprite in group:
            sprite.kill()             

main_menu()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pause_menu()
    
    if pygame.time.get_ticks() - level_start_time > 3000:
        if level < 6:
            if random.random() < ENEMY_GENERATION_THRESHOLDS['ENEMY_1']:
                enemy_1 = Enemy_1()
                enemies_p['enemies_1'].add(enemy_1)
                all_sprites.add(enemy_1)
                enemies.add(enemy_1)
            if level > 1:
                if random.random() < ENEMY_GENERATION_THRESHOLDS['ENEMY_2']:
                    enemy_2 = Enemy_2()
                    enemies_p['enemies_2'].add(enemy_2)
                    all_sprites.add(enemy_2)
                    enemies.add(enemy_2)
            if level > 2:
                if random.random() < ENEMY_GENERATION_THRESHOLDS['ENEMY_3']:
                    enemy_3 = Enemy_3()
                    enemies_p['enemies_3'].add(enemy_3)
                    all_sprites.add(enemy_3)
                    enemies.add(enemy_3)
            if level > 3:
                if random.random() < ENEMY_GENERATION_THRESHOLDS['ENEMY_4']:
                    enemy_4 = Enemy_4(enemies)
                    enemies_p['enemies_4'].add(enemy_4)
                    all_sprites.add(enemy_4)
                    enemies.add(enemy_4)
            if level == 5:
                if BOSS_GENERATION_ONCE == False:
                    enemy_5 = Boss_1()
                    enemies_p['enemies_5'].add(enemy_5)
                    all_sprites.add(enemy_5)
                    BOSS_GENERATION_ONCE = True
        elif level > 5:
            if random.random() < ENEMY_GENERATION_THRESHOLDS['ENEMY_5']:
                enemy_6 = Enemy_5()
                enemies_p['enemies_6'].add(enemy_6)
                all_sprites.add(enemy_6)
                enemies.add(enemy_6)
            if level > 6:
                if random.random() < ENEMY_GENERATION_THRESHOLDS['ENEMY_6']:
                    enemy_7 = Enemy_6()
                    enemies_p['enemies_7'].add(enemy_7)
                    all_sprites.add(enemy_7)
                    enemies.add(enemy_7)
            if level > 7:
                if random.random() < ENEMY_GENERATION_THRESHOLDS['ENEMY_7']:
                    enemy_8 = Enemy_7()
                    enemies_p['enemies_8'].add(enemy_8)
                    all_sprites.add(enemy_8)
                    enemies.add(enemy_8)
            if level > 8:
                if random.random() < ENEMY_GENERATION_THRESHOLDS['ENEMY_8']:
                    enemy_9 = Enemy_8(enemies)
                    enemies_p['enemies_9'].add(enemy_9)
                    all_sprites.add(enemy_9)
                    enemies.add(enemy_9)
            if level > 9:
                if random.random() < ENEMY_GENERATION_THRESHOLDS['ENEMY_9']: 
                    enemy_10 = Enemy_9()
                    enemies_p['enemies_10'].add(enemy_10)
                    all_sprites.add(enemy_10)

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

    for group in items.values():
        for item in group:
            screen.blit(item.surf, item.rect)

    for enemy_bullet in enemy_bullets:
        screen.blit(enemy_bullet.surf, enemy_bullet.rect)
    
    check_bullet_hit(bullets, enemies_p['enemies_1'], 1, 0.3, 0.05, Explosion_1)
    check_bullet_hit(bullets, enemies_p['enemies_2'], 3, 0.06, 0.09, Explosion_2)
    check_bullet_hit(bullets, enemies_p['enemies_3'], 5, 0.09, 0.1, Explosion_3)
    check_bullet_hit(bullets, enemies_p['enemies_4'], 2, 0.02, 0.15, Explosion_4)
    check_bullet_hit(bullets, enemies_p['enemies_5'], 2, 0.3, 0.5, Explosion_5)
    check_bullet_hit(bullets, enemies_p['enemies_6'], 2, 0.1, 0.1, Explosion_6)
    check_bullet_hit(bullets, enemies_p['enemies_7'], 4, 0.15, 0.1, Explosion_7)
    check_bullet_hit(bullets, enemies_p['enemies_8'], 6, 0.15, 0.1, Explosion_8)
    check_bullet_hit(bullets, enemies_p['enemies_9'], 3, 0.15, 0.1, Explosion_9)
    check_bullet_hit(bullets, enemies_p['enemies_10'], 10, 0.3, 0.3, Explosion_10)
    
    for item_type in items.keys():
        item_collision(player, item_type)

    enemy_groups = [(enemies_p['enemies_1'], 1 ), (enemies_p['enemies_2'], 1), (enemies_p['enemies_3'], 2), (enemies_p['enemies_4'], 1), (enemies_p['enemies_5'], 5), (enemies_p['enemies_6'], 1), (enemies_p['enemies_7'], 2), (enemies_p['enemies_8'], 3), (enemies_p['enemies_9'], 1), (enemies_p['enemies_10'], 3)]
    for group, damage in enemy_groups:
        if pygame.sprite.spritecollideany(player, group):
            if not player.invincible and not player.invincible_shield:
                player.lives -= damage
                player.invincible = True
                player.last_hit_time = pygame.time.get_ticks()

    if pygame.sprite.spritecollideany(player, enemy_bullets):
        if not player.invincible and not player.invincible_shield:
            player.lives -= 1 
            player.invincible = True 
            player.last_hit_time = pygame.time.get_ticks() 

    if player.invincible and pygame.time.get_ticks() - player.last_hit_time > 3000:
        player.invincible = False

    if player.invincible_shield and pygame.time.get_ticks() - player.shield_start_time > 5000:
        player.invincible_shield = False

    if player.lives <= 0 or level > 20:
        game_over_screen()
    
    if score > 75:
        action = stage_clear_screen(level, score)
        if action == 'next':
            reset_enemies()
            level += 1
            score = 0
            player.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-30)
            player.lives = max_lives
            level_start_time = pygame.time.get_ticks()  # 更新關卡開始時間
        elif action == 'menu':
            main_menu()
        elif action == 'previous':
            reset_enemies()
            level -= 1
            score = 0
            player.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-30)
            player.lives = max_lives
            level_start_time = pygame.time.get_ticks()  # 更新關卡開始時間

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

    lives_text = font.render('Lives: {}'.format(player.lives), True, (255, 255, 255))
    screen.blit(lives_text, (10, 70)) 

    pygame.display.flip()
    clock.tick(185) 

pygame.quit()
sys.exit()