import pygame
import random
import math
import os
import sys

# Helper for PyInstaller: find files whether running as .py or exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class HealingItem:
    #dictionary to map item color (and image name cause im smart like that) to its healing value
    HEAL_VALUES = {
        "Red": 50,
        "Yellow": 20,
        "Blue": 70
    }
    #offset the visual bobbing motion since it's a single image
    BOB_AMPLITUDE = 3    # Pixels up and down
    BOB_SPEED = 0.1      #how fast we movin

    def __init__(self, item_name, images, ground_level, min_x, max_x):
        self.name = item_name
        self.heal_amount = self.HEAL_VALUES.get(item_name, 0)
        
        #load the image 
        self.image = images[item_name]
        self.image_rect = self.image.get_rect()
        
        # positioning
        # The rect width is subtracted to prevent the item from spawning off screen on the right
        self.x = random.uniform(min_x, max_x - self.image_rect.width) 
        self.base_y = ground_level - self.image_rect.height - 10
        self.y = self.base_y
        
        #bobbing control
        self.bob_timer = random.uniform(0, math.pi * 2)
        
        #boss stealing movement controls
        self.boss_steal_timer =0 #is set in index so it's okay
        self.is_stolen = False    #flag so it will start moving towards the boss
        self.target = None        #will hold the boss' location reference
        self.move_speed =4.0     # HOW FAST WE GOING
        # boss is scaled 110 by 100 but needs offset
        self.boss_center_offset_x = 90
        self.boss_center_offset_y =90


    def update(self):
        #update movement if stolen
        if self.is_stolen and self.target:
            
            #calc boss center position(doesnt need to be exactly center but needs to be in boss' location )
            target_x = self.target.x + self.boss_center_offset_x
            target_y = self.target.y + self.boss_center_offset_y
            
            dx = target_x - self.x
            dy = target_y - self.y
            # F-CKKK math
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > self.move_speed:
                direction_x = dx / distance
                direction_y = dy / distance
                
                self.x += direction_x * self.move_speed
                self.y += direction_y * self.move_speed
                
            else:
                #item has reached the boss then
                #stop and align for colissions
                self.x = target_x - self.image_rect.width / 2
                self.y = target_y - self.image_rect.height / 2

        #update bobbing motion(only if not stolen)
        else:
            self.bob_timer += self.BOB_SPEED
            bob_offset = math.sin(self.bob_timer) * self.BOB_AMPLITUDE
            self.y = self.base_y + bob_offset

        #update rect for collision check
        self.image_rect.topleft = (self.x, self.y)


    def draw(self, screen, camera_x, camera_y, zoom):
        # Apply zoom and camera offset for drawing
        draw_x = (self.x - camera_x) * zoom
        draw_y = (self.y - camera_y) * zoom
        
        #To draw with correct zoom
        zoomed_image = pygame.transform.rotozoom(self.image, 0, zoom)
        screen.blit(zoomed_image, (draw_x, draw_y))


    def draw_hitbox(self, screen, camera_x, camera_y, zoom):
        
        collision_rect = self.get_hitbox(zoom)
        
        #shift the collision rect coordinates by the camera offset to get screen coordinates(figured this out LATE)
        screen_rect = pygame.Rect(
            collision_rect.x - camera_x * zoom,
            collision_rect.y - camera_y * zoom,
            collision_rect.width, 
            collision_rect.height
        )
        
        #the colour so i could diferenciate b4
        pygame.draw.rect(screen, (255, 0, 255), screen_rect, 1)


    def get_hitbox(self, zoom): 
        world_rect = self.image_rect 
        
        return pygame.Rect(
            self.x * zoom, 
            self.y * zoom, 
            world_rect.width * zoom, 
            world_rect.height * zoom
        )
    
    
    @classmethod
    def load_item_images(cls):
        #not using spritehseet cause it isnt one
        item_images = {}
        for name in cls.HEAL_VALUES.keys():
            try:
                #load and as png with transparenct
                img = pygame.image.load(resource_path(f'{name}.png')).convert_alpha() 
                img = pygame.transform.scale(img, (24, 24))
                item_images[name] = img
            except pygame.error:
                print(f"Error loading healing item image: {name}.png. Using placeholder.")
                item_images[name] = pygame.Surface((24, 24), pygame.SRCALPHA)
                item_images[name].fill((255, 0, 255)) # Pink placeholder
        return item_images
