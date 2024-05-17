import random
from config import *
from shared import enemy_bullets, enemies, all_sprites
from enemybullet import EnemyBullet_1, EnemyBullet_2, EnemyBullet_3, EnemyBullet_4, EnemyBullet_5, EnemyBullet_6, EnemyBullet_7, EnemyBullet_8, EnemyBullet_9, EnemyBullet_10, EnemyBullet_11, EnemyBullet_12, EnemyBullet_13, EnemyBullet_14, EnemyBullet_15

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
        super().__init__('img/enemy/lv1_to_5/base/Scout_assets/Scout_frame_1.png', 'img/enemy/lv1_to_5/Shield/Scout_assets/Scout_Shield_frame_', (39.4, 42.8), (37.4, 40.8), 2, enemy_hp["enemies_1"], 14)
    
    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_1, 0.002)

class Enemy_2(Enemy):
    def __init__(self):
        super().__init__('img/enemy/lv1_to_5/base/Torpedo_assets/Torpedo_frame_1.png', 'img/enemy/lv1_to_5/Shield/Torpedo_assets/Torpedo_frame_', None, None, 1, enemy_hp["enemies_2"], 11)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_2, 0.002)

class Enemy_3(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv1_to_5/base/Frigate_assets/Frigate_frame_1.png', 'img/enemy/lv1_to_5/Shield/Frigate_assets/Frigate_Shield_frame_', None, None, 4, enemy_hp["enemies_3"], 39)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_2, 0.000001)

class Enemy_4(Enemy):

    targets = [] 

    def __init__(self, enemies):
        super().__init__('img/enemy/lv1_to_5/base/Support_assets/Support_frame_1.png', None, None, None, 2, enemy_hp["enemies_4"])
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
       super().__init__('img/enemy/lv6_to_10/base/Scout_assets/Scout_frame_1.png', 'img/enemy/lv6_to_10/Shield/Scout_assets/Scout_frame__', (36, 33), (36, 33), 2, enemy_hp["enemies_6"], 19)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_5, 0.003)

class Enemy_6(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv6_to_10/base/Torpedo_assets/Torpedo_frame_1.png', 'img/enemy/lv6_to_10/Shield/Torpedo_assets/Torpedo_frame_', None, None, 1, enemy_hp["enemies_7"], 9)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_6, 0.003)

class Enemy_7(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv6_to_10/base/Frigate_assets/Frigate_frame_1.png', 'img/enemy/lv6_to_10/Shield/Frigate_assets/Frigate_frame_', None, None, 4, enemy_hp["enemies_8"], 9)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_5, 0.003)

class Enemy_8(Enemy):

    targets = [] 

    def __init__(self, enemies):
        super().__init__('img/enemy/lv6_to_10/base/Support_assets/Support_frame_1.png', None, None, None, 2, enemy_hp["enemies_9"])
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
       super().__init__('img/enemy/lv6_to_10/base/Battlecruiser_assets/Battlecruiser_frame_1.png', 'img/enemy/lv6_to_10/Shield/Battlecruiser_assets/Battlecruiser_frame_', None, None, 0, enemy_hp["enemies_10"], 9)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_7, 0.003)

class Enemy_10(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv11_to_15/base/Scout_assets/Scout_frame_1.png', 'img/enemy/lv11_to_15/Shields/Scout_assets/Scout_frame_', None, None, 1, enemy_hp["enemies_12"], 14)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_10, 0.003)

class Enemy_11(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv11_to_15/base/Bomber_assets/Bomber_frame_1.png', 'img/enemy/lv11_to_15/Shields/Bomber_assets/Bomber_frame_', None, None, 2, enemy_hp["enemies_13"], 11)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_11, 0.003)

class Enemy_12(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv11_to_15/base/Torpedo_assets/Torpedo_frame_1.png', 'img/enemy/lv11_to_15/Shields/Torpedo_assets/Torpedo_frame_', None, None, 1, enemy_hp["enemies_14"], 9)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_12, 0.003)

class Enemy_13(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv11_to_15/base/Frigate_assets/Frigate_frame_1.png', 'img/enemy/lv11_to_15/Shields/Frigate_assets/Frigate_frame_', None, None, 4, enemy_hp["enemies_15"], 11)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_10, 0.003)

class Enemy_14(Enemy):

    targets = [] 

    def __init__(self, enemies):
        super().__init__('img/enemy/lv11_to_15/base/Support_assets/Support_frame_1.png', None, None, None, 2, enemy_hp["enemies_16"])
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

class Enemy_15(Enemy):
    def __init__(self):
       super().__init__('img/enemy/lv11_to_15/base/Battlecruiser_assets/Battlecruiser_frame_1.png', 'img/enemy/lv11_to_15/Shields/Battlecruiser_assets/Battlecruiser_frame_', None, None, 0, enemy_hp["enemies_17"], 12)

    def update(self, pressed_keys=None, mouse_pos=None):
        super().update(EnemyBullet_13, 0.03)

class Boss_1(Enemy):
    def __init__(self):
        super().__init__('img/enemy/lv1_to_5/base/Battlecruiser_assets/Battlecruiser_frame_1.png', None, None, (108,132), 2, enemy_hp["enemies_5"])
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

        self.maxhp = 50000
    
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

class Boss_2(Enemy):
    def __init__(self):
        super().__init__('img/enemy/lv6_to_10/base/Dreadnought_assets/Dreadnought_frame_1.png', None, None, (102,147), 2, enemy_hp["enemies_11"])
        self.original_image = pygame.image.load('img/enemy/lv6_to_10/base/Dreadnought_assets/Dreadnought_frame_1.png').convert_alpha()
        self.rect.midtop = (0, 0) 
        self.laser_cooldown = 2000  
        self.laser_charging = False
        self.laser_firing = False
        self.scatter_cooldown = 700 
        self.laser_timer = pygame.time.get_ticks()
        self.scatter_timer = pygame.time.get_ticks()
        self.rapid_fire_timer = pygame.time.get_ticks()
        self.rapid_fire_end_time = pygame.time.get_ticks()
        self.rapid_fire_cooldown = 20000
        self.is_rapid_firing = False
        self.speed = 2 
        self.direction = 1  
        self.move_phase = 0  # 0: right, 1: down, 2: left, 3: up
        self.laser_angle = 0
        self.fire_scatter_angle = 0
        self.rotated_images = {
            0: pygame.transform.rotate(self.original_image, -90),
            1: self.original_image,
            2: pygame.transform.rotate(self.original_image, 180),
            3: pygame.transform.rotate(self.original_image, 90)
        }

        self.maxhp = 200000

    def update(self, pressed_keys=None, mouse_pos=None):
        self.move_sideways()
        self.fire_scatter_bullets()
        self.fire_laser()

        if self.hp <= 0:
            self.kill()
        
        if not self.is_rapid_firing and pygame.time.get_ticks() - self.rapid_fire_timer >= self.rapid_fire_cooldown:
            self.is_rapid_firing = True
            self.rapid_fire_start_time = pygame.time.get_ticks()
            self.rapid_fire_end_time = pygame.time.get_ticks()

        if self.is_rapid_firing:
            if pygame.time.get_ticks() - self.rapid_fire_end_time >= 5000:
                self.is_rapid_firing = False
                self.rapid_fire_timer = pygame.time.get_ticks()

    def move_sideways(self):
        if self.move_phase == 0:  # Moving right
            if self.rect.right >= SCREEN_WIDTH + 5:
                self.move_phase = 1
                self.direction = 0
            else:
                self.rect.move_ip(self.speed, 0)
                self.surf = self.rotated_images[self.direction]
        elif self.move_phase == 1:  # Moving down
            if self.rect.bottom >= SCREEN_HEIGHT + 50:
                self.move_phase = 2
                self.direction = 2
            else:
                self.rect.move_ip(0, self.speed)
                self.surf = self.rotated_images[self.direction]
        elif self.move_phase == 2:  # Moving left
            if self.rect.left <= 0:
                self.move_phase = 3
                self.direction = 3
            else:
                self.rect.move_ip(-self.speed, 0)
                self.surf = self.rotated_images[self.direction]
        elif self.move_phase == 3:  # Moving up
            if self.rect.top <= 0:
                self.move_phase = 0
                self.direction = 1
            else:
                self.rect.move_ip(0, -self.speed)
                self.surf = self.rotated_images[self.direction]

    def fire_laser(self):
        now = pygame.time.get_ticks()
        bullet = EnemyBullet_9(self)
        if now - self.laser_timer >= self.laser_cooldown or (self.is_rapid_firing and pygame.time.get_ticks() - self.rapid_fire_start_time >= 100):
            self.laser_timer = now
            self.rapid_fire_start_time = pygame.time.get_ticks()
            if self.direction == 0:
                self.laser_angle = -90
                bullet.velocity = pygame.math.Vector2(-3, 0)
            elif self.direction == 1:
                self.laser_angle = 0
                bullet.velocity = pygame.math.Vector2(0, 3)
            elif self.direction == 2:
                self.laser_angle = 180
                bullet.velocity = pygame.math.Vector2(0, -3)
            elif self.direction == 3:
                self.laser_angle = 90
                bullet.velocity = pygame.math.Vector2(3, 0)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)

    def fire_scatter_bullets(self):
        now = pygame.time.get_ticks()
        if now - self.scatter_timer >= self.scatter_cooldown:
            self.scatter_timer = now
            if self.direction == 0:
                for angle in [-225, -270, -315] :
                    bullet = EnemyBullet_8(self)
                    bullet.velocity = pygame.math.Vector2(0, 3).rotate(angle)
                    self.fire_scatter_angle = -90
                    bullet.surf = pygame.transform.rotate(bullet.original_image, self.fire_scatter_angle)
                    enemy_bullets.add(bullet)
                    all_sprites.add(bullet)
            elif self.direction == 1:
                for angle in [45, 0, -45]:
                    bullet = EnemyBullet_8(self)
                    bullet.velocity = pygame.math.Vector2(0, 3).rotate(angle)
                    self.fire_scatter_angle = 0
                    bullet.surf = pygame.transform.rotate(bullet.original_image, self.fire_scatter_angle)
                    enemy_bullets.add(bullet)
                    all_sprites.add(bullet)
            elif self.direction == 2:
                for angle in [225, 180, 135]:
                    bullet = EnemyBullet_8(self)
                    bullet.velocity = pygame.math.Vector2(0, 3).rotate(angle)
                    self.fire_scatter_angle = 180
                    bullet.surf = pygame.transform.rotate(bullet.original_image, self.fire_scatter_angle)
                    enemy_bullets.add(bullet)
                    all_sprites.add(bullet)
            elif self.direction == 3:
                for angle in [-135, -90, -45]:
                    bullet = EnemyBullet_8(self)
                    bullet.velocity = pygame.math.Vector2(0, 3).rotate(angle)
                    self.fire_scatter_angle = 90
                    bullet.surf = pygame.transform.rotate(bullet.original_image, self.fire_scatter_angle)
                    enemy_bullets.add(bullet)
                    all_sprites.add(bullet)

class Boss_3(Enemy):
    def __init__(self):
        super().__init__('img/enemy/lv11_to_15/base/Dreadnought_assets/Dreadnought_frame_1.png', None, None, None, 2, enemy_hp["enemies_18"])
        self.original_image = pygame.image.load('img/enemy/lv11_to_15/base/Dreadnought_assets/Dreadnought_frame_1.png').convert_alpha()
        self.rect.midtop = (0, 0) 
        self.laser_cooldown = 2000  
        self.laser_charging = False
        self.laser_firing = False
        self.scatter_cooldown = 700 
        self.laser_timer = pygame.time.get_ticks()
        self.scatter_timer = pygame.time.get_ticks()
        self.rapid_fire_timer = pygame.time.get_ticks()
        self.rapid_fire_end_time = pygame.time.get_ticks()
        self.rapid_fire_cooldown = 20000
        self.is_rapid_firing = False
        self.speed = 2 
        self.direction = 1  
        self.move_phase = 0  # 0: right, 1: down, 2: left, 3: up
        self.laser_angle = 0
        self.fire_scatter_angle = 0
        self.rotated_images = {
            0: pygame.transform.rotate(self.original_image, -90),
            1: self.original_image,
            2: pygame.transform.rotate(self.original_image, 180),
            3: pygame.transform.rotate(self.original_image, 90)
        }

        self.scatter_skill_timer = pygame.time.get_ticks()
        self.scatter_skill_cooldown = 15000  # 15 seconds
        self.scatter_skill_active = False
        self.scatter_skill_shooting_time = 0
        self.scatter_skill_start_time = 0
        self.condition_met_time = 0

        self.maxhp = 300000

    def update(self, pressed_keys=None, mouse_pos=None):
        self.move_sideways()
        self.fire_scatter_bullets()
        self.fire_laser()

        if self.hp <= 0:
            self.kill()
        
        if not self.is_rapid_firing and pygame.time.get_ticks() - self.rapid_fire_timer >= self.rapid_fire_cooldown:
            self.is_rapid_firing = True
            self.rapid_fire_start_time = pygame.time.get_ticks()
            self.rapid_fire_end_time = pygame.time.get_ticks()

        if self.is_rapid_firing:
            if pygame.time.get_ticks() - self.rapid_fire_end_time >= 5000:
                self.is_rapid_firing = False
                self.rapid_fire_timer = pygame.time.get_ticks()
        
        if not self.scatter_skill_active and pygame.time.get_ticks() - self.scatter_skill_timer >= self.scatter_skill_cooldown:
            self.scatter_skill_active = True
            self.direction = 0
            self.scatter_skill_start_time = pygame.time.get_ticks()
        
        if self.scatter_skill_active:
            print("scatter_skill_active")
            self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)  # move to center
            if pygame.time.get_ticks() - self.scatter_skill_start_time >= 1000:  # every second
                self.direction = (self.direction + 1) % 4
                self.surf = self.rotated_images[self.direction]
                self.scatter_skill_start_time = pygame.time.get_ticks()  # reset timer
        
            if self.direction == 3:
                self.condition_met_time = pygame.time.get_ticks()  # record the time when the condition is met

            if self.condition_met_time > 0 and pygame.time.get_ticks() - self.condition_met_time >= 1000:
                self.scatter_skill_active = False
                self.rect.midtop = (0, 0)  # move back to edge
                self.scatter_skill_timer = pygame.time.get_ticks()  # reset cooldown timer
                self.condition_met_time = 0  # reset the condition met time

    def move_sideways(self):
        if not self.scatter_skill_active:
            if self.move_phase == 0:  # Moving right
                if self.rect.right >= SCREEN_WIDTH:
                    self.move_phase = 1
                    self.direction = 0
                else:
                    self.rect.move_ip(self.speed, 0)
                    self.surf = self.rotated_images[self.direction]
            elif self.move_phase == 1:  # Moving down
                if self.rect.bottom >= SCREEN_HEIGHT:
                    self.move_phase = 2
                    self.direction = 2
                else:
                    self.rect.move_ip(0, self.speed)
                    self.surf = self.rotated_images[self.direction]
            elif self.move_phase == 2:  # Moving left
                if self.rect.left <= 0:
                    self.move_phase = 3
                    self.direction = 3
                else:
                    self.rect.move_ip(-self.speed, 0)
                    self.surf = self.rotated_images[self.direction]
            elif self.move_phase == 3:  # Moving up
                if self.rect.top <= 0:
                    self.move_phase = 0
                    self.direction = 1
                else:
                    self.rect.move_ip(0, -self.speed)
                    self.surf = self.rotated_images[self.direction]

    def fire_laser(self):
        now = pygame.time.get_ticks()
        bullet = EnemyBullet_15(self)
        if now - self.laser_timer >= self.laser_cooldown or (self.is_rapid_firing and pygame.time.get_ticks() - self.rapid_fire_start_time >= 100):
            self.laser_timer = now
            self.rapid_fire_start_time = pygame.time.get_ticks()
            if self.direction == 0:
                self.laser_angle = -90
                bullet.velocity = pygame.math.Vector2(-3, 0)
            elif self.direction == 1:
                self.laser_angle = 0
                bullet.velocity = pygame.math.Vector2(0, 3)
            elif self.direction == 2:
                self.laser_angle = 180
                bullet.velocity = pygame.math.Vector2(0, -3)
            elif self.direction == 3:
                self.laser_angle = 90
                bullet.velocity = pygame.math.Vector2(3, 0)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)

    def fire_scatter_bullets(self):
        now = pygame.time.get_ticks()
        if now - self.scatter_timer >= self.scatter_cooldown or (self.scatter_skill_active and now - self.scatter_skill_shooting_time >= 200):
            self.scatter_timer = now
            if self.direction == 0:
                for angle in [-225, -270, -315] :
                    bullet = EnemyBullet_14(self)
                    bullet.velocity = pygame.math.Vector2(0, 3).rotate(angle)
                    self.fire_scatter_angle = -90
                    bullet.surf = pygame.transform.rotate(bullet.original_image, self.fire_scatter_angle)
                    enemy_bullets.add(bullet)
                    all_sprites.add(bullet)
            elif self.direction == 1:
                for angle in [45, 0, -45]:
                    bullet = EnemyBullet_14(self)
                    bullet.velocity = pygame.math.Vector2(0, 3).rotate(angle)
                    self.fire_scatter_angle = 0
                    bullet.surf = pygame.transform.rotate(bullet.original_image, self.fire_scatter_angle)
                    enemy_bullets.add(bullet)
                    all_sprites.add(bullet)
            elif self.direction == 2:
                for angle in [225, 180, 135]:
                    bullet = EnemyBullet_14(self)
                    bullet.velocity = pygame.math.Vector2(0, 3).rotate(angle)
                    self.fire_scatter_angle = 180
                    bullet.surf = pygame.transform.rotate(bullet.original_image, self.fire_scatter_angle)
                    enemy_bullets.add(bullet)
                    all_sprites.add(bullet)
            elif self.direction == 3:
                for angle in [-135, -90, -45]:
                    bullet = EnemyBullet_14(self)
                    bullet.velocity = pygame.math.Vector2(0, 3).rotate(angle)
                    self.fire_scatter_angle = 90
                    bullet.surf = pygame.transform.rotate(bullet.original_image, self.fire_scatter_angle)
                    enemy_bullets.add(bullet)
                    all_sprites.add(bullet)
            self.scatter_skill_shooting_time = pygame.time.get_ticks()