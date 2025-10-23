import pygame
import random
import math #math needed for angle calculation(i KNOWWWWW)
import os
import sys

# helper to find the correct path when bundled with PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, world_width, y_min, y_max, speed=5, scale=1, type="straight", target_pos=(0, 0)):
        super().__init__()
        
        #sprite step up and erro handling
        try:
            self.original_image = pygame.image.load(resource_path("arm_projectile.png")).convert_alpha()
        except pygame.error as e:
            print(f"Error loading projectile image: {e}. Using fallback circle.")
            self.original_image = pygame.Surface([16, 16], pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 100, 0), (8, 8), 8)
        
        self.scale = scale
        self.image = pygame.transform.scale(self.original_image, 
                                            (self.original_image.get_width() * scale, 
                                             self.original_image.get_height() * scale))
        self.rect = self.image.get_rect()

        self.world_width = world_width
        self.y_min = y_min
        self.y_max = y_max
        self.damage = 5

        #movement setup
        self.type = type
        self.speed = abs(speed)
        
        #intiial positions
        self.x = -self.rect.width / scale 
        self.y = random.randint(self.y_min, self.y_max)
        self.start_y = self.y #base y for jumping
        self.initial_x = self.x #base x for trajectory checks
        
        self.rect.topleft = (self.x, self.y)

        #targetting and jumping projectiles setup
        if self.type == "targeted":
            player_x, player_y = target_pos
            #calculate angle to target so it moves towards the player position
            angle = math.atan2(player_y - self.y, player_x - self.x)
            self.speed_x = self.speed * math.cos(angle)
            self.speed_y = self.speed * math.sin(angle)
        elif self.type == "jumping":
            #set up parameters for a sine wave or simple arc
            self.amplitude = 50 * self.scale #max height of the jump/wave as necessary
            self.frequency = 0.01 / self.scale # How tight the wave is (smaller is wider jump REMEMBER THIS)

        #hitbox adjustments cause idk why mine keep spawning off, prob zoom issues
        self.hitbox_size_modifier_w = 40 
        self.hitbox_size_modifier_h = 55
        self.hitbox_shift_x = 25 
        self.hitbox_shift_y = -10


    def update(self):
        
        if self.type == "straight":
            self.x += self.speed
            
        elif self.type == "jumping":
            self.x += self.speed
            #using a sine wave for a clean jumpcpattern
            # x position dictates the point in the wave
            self.y = self.start_y + self.amplitude * math.sin((self.x - self.initial_x) * self.frequency)

        elif self.type == "targeted":
            self.x += self.speed_x
            self.y += self.speed_y
            
        self.rect.topleft = (self.x, self.y)

    def is_off_screen(self, world_width):
        #check if the projectile is too far past the right or bottom
        return self.x > world_width or self.y < self.y_min - 100 or self.y > self.y_max + 100

    def get_hitbox(self, zoom):

        full_w = self.image.get_width()
        full_h = self.image.get_height()

        scaled_modifier_w = self.hitbox_size_modifier_w * zoom
        scaled_modifier_h = self.hitbox_size_modifier_h * zoom
        
        w = full_w - scaled_modifier_w
        h = full_h - scaled_modifier_h
        

        offset_x = (full_w - w) / 2 + (self.hitbox_shift_x * zoom)
        offset_y = (full_h - h) / 2 + (self.hitbox_shift_y * zoom)
        
        # scaled rec
        hitbox_x = (self.x * zoom) + offset_x
        hitbox_y = (self.y * zoom) + offset_y
        
        return pygame.Rect(hitbox_x, hitbox_y, w, h)

    def draw(self, screen, camera_x, camera_y, zoom):
        
        draw_x = (self.x - camera_x) * zoom
        draw_y = (self.y - camera_y) * zoom
        screen.blit(self.image, (draw_x, draw_y))
        

    def draw_hitbox(self, screen, camera_x, camera_y, zoom):
        scaled_hitbox = self.get_hitbox(zoom)
        
        draw_x = scaled_hitbox.x - (camera_x * zoom)
        draw_y = scaled_hitbox.y - (camera_y * zoom)
        
        draw_rect = pygame.Rect(draw_x, draw_y, scaled_hitbox.width, scaled_hitbox.height)
        
        pygame.draw.rect(screen, (0, 255, 0), draw_rect, 2)
