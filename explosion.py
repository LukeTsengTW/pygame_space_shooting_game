import pygame

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

class Explosion_11(Explosion):
    def __init__(self, center):
        images = []
        for i in range(1, 18):
            image = pygame.image.load(f'img/enemy/lv6_to_10/base/Dreadnought_assets/Dreadnought_frame_{i}.png').convert_alpha()
            original_width, original_height = image.get_size()
            scaled_width = int(original_width * 1.5)
            scaled_height = int(original_height * 1.5)
            image = pygame.transform.scale(image, (scaled_width, scaled_height))
            images.append(image)
        super().__init__(center, images)

class Explosion_12(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv11_to_15/base/Scout_assets/Scout_frame_{i}.png').convert_alpha() for i in range(1,10)]
        super().__init__(center, images)

class Explosion_13(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv11_to_15/base/Bomber_assets/Bomber_frame_{i}.png').convert_alpha() for i in range(1,10)]
        super().__init__(center, images)

class Explosion_14(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv11_to_15/base/Torpedo_assets/Torpedo_frame_{i}.png').convert_alpha() for i in range(1,8)]
        super().__init__(center, images)

class Explosion_15(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv11_to_15/base/Frigate_assets/Frigate_frame_{i}.png').convert_alpha() for i in range(1,10)]
        super().__init__(center, images)

class Explosion_16(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv11_to_15/base/Support_assets/Support_frame_{i}.png').convert_alpha() for i in range(1,8)]
        super().__init__(center, images)

class Explosion_17(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv11_to_15/base/Battlecruiser_assets/Battlecruiser_frame_{i}.png').convert_alpha() for i in range(1,13)]
        super().__init__(center, images)

class Explosion_18(Explosion):
    def __init__(self, center):
        images = [pygame.image.load(f'img/enemy/lv11_to_15/base/Dreadnought_assets/Dreadnought_frame_{i}.png').convert_alpha() for i in range(1,13)]
        super().__init__(center, images)