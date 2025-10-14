import pygame
from sys import exit

pygame.init()

class SpriteSheet():
    def __init__(self, image):
        self.sheet = image
    
    def get_image(self, frame, width, height, scale):
        # Create a fully transparent surface
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        # Copy the frame from the sprite sheet
        image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))
        # Scale while keeping transparency
        image = pygame.transform.scale(image, (width*scale, height*scale))
        return image
