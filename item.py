from config import *

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