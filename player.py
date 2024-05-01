from config import *
from shared import bullets, all_sprites

class Player(pygame.sprite.Sprite):
    global player_bullet_angle, max_lives, PLAYER_SPEED, BULLET_SPEED
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
        self.coin = 0
        self.damage = 50
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

        self.control = 0

        self.out_of_game = True

    def activate_shield(self):
        self.invincible_shield = True
        self.shield_start_time = pygame.time.get_ticks()

    def update(self, pressed_keys, mouse_pos):
        if self.out_of_game:
            pygame.mouse.set_visible(True)
        elif not self.out_of_game and self.control == 1:
            pygame.mouse.set_visible(False)
        if self.control == 0:
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
            self.shield_rect = self.shield_surf.get_rect(center = (self.rect.centerx, self.rect.centery))
            screen.blit(self.shield_surf, self.shield_rect)

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