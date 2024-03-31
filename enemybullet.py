from config import *

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
        super().__init__(enemy, 'img/enemy/lv6_to_10/Projectile/Bolt_assets/Bolt_frame_', (10,14), 7)

class EnemyBullet_6(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv6_to_10/Projectile/Torpedo_assets/Torpedo_frame_', (14,34), 4)

class EnemyBullet_7(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv6_to_10/Projectile/Ray_assets/Ray_frame_', None, 5)

class EnemyBullet_8(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv6_to_10/Projectile/Bolt_assets/Bolt_frame_', (20, 28), 7)
        self.original_image = self.surf
        self.velocity = pygame.math.Vector2(0, 0)

    def update(self, pressed_keys=None, mouse_pos=None):
        self.pos_y += self.velocity.y
        self.pos_x += self.velocity.x
        self.rect.y = int(self.pos_y)
        self.rect.x = int(self.pos_x)
        if self.rect.top > SCREEN_HEIGHT + 200 or self.rect.bottom < -200 or self.rect.left < -200 or self.rect.right > SCREEN_WIDTH + 200:
            self.kill()

class EnemyBullet_9(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv6_to_10/Projectile/Ray_assets/Ray_frame_', (65, 180), 5)
        self.velocity = pygame.math.Vector2(0, 0)
        self.boss = enemy
    def update(self, pressed_keys=None, mouse_pos=None):
        self.surf = pygame.transform.rotate(self.images[self.index], self.boss.laser_angle)
        self.pos_y += self.velocity.y
        self.pos_x += self.velocity.x
        self.rect.y = int(self.pos_y)
        self.rect.x = int(self.pos_x)
        if self.rect.top > SCREEN_HEIGHT + 200 or self.rect.bottom < -200 or self.rect.left < -200 or self.rect.right > SCREEN_WIDTH + 200:
            self.kill()

class EnemyBullet_10(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv11_to_15/Projectiles/Bullet_assets/Bullet_frame_', None, 9)

class EnemyBullet_11(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv11_to_15/Projectiles/Bomb_assets/Bomb_frame_', None, 17)

class EnemyBullet_12(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv11_to_15/Projectiles/Rocket_assets/Rocket_frame_', None, 7)

class EnemyBullet_13(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv11_to_15/Projectiles/Ray_assets/Ray_frame_', None, 5)

class EnemyBullet_14(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv11_to_15/Projectiles/Bullet_assets/Bullet_frame_', (20, 32), 9)
        self.original_image = self.surf
        self.velocity = pygame.math.Vector2(0, 0)

    def update(self, pressed_keys=None, mouse_pos=None):
        self.pos_y += self.velocity.y
        self.pos_x += self.velocity.x
        self.rect.y = int(self.pos_y)
        self.rect.x = int(self.pos_x)
        if self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.kill()

class EnemyBullet_15(EnemyBullet):
    def __init__(self, enemy):
        super().__init__(enemy, 'img/enemy/lv11_to_15/Projectiles/Ray_assets/Ray_frame_', (24, 152), 5)
        self.velocity = pygame.math.Vector2(0, 0)
        self.boss = enemy
    def update(self, pressed_keys=None, mouse_pos=None):
        self.surf = pygame.transform.rotate(self.images[self.index], self.boss.laser_angle)
        self.pos_y += self.velocity.y
        self.pos_x += self.velocity.x
        self.rect.y = int(self.pos_y)
        self.rect.x = int(self.pos_x)
        if self.rect.top > SCREEN_HEIGHT + 200 or self.rect.bottom < -200 or self.rect.left < -200 or self.rect.right > SCREEN_WIDTH + 200:
            self.kill()