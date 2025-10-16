import pygame
from settings import SCALE_FACTOR

def load_background_layers():

    #background layers from farthest to nearest, the farthest moves slower to give the parallax effect.
    bg_layers = [
        ("Sky.png", 0.2),
        ("DownLayer.png", 0.4),
        ("MiddleLayer.png", 0.6),
        ("Light.png", 0.8),
        ("TopLayer.png", 1.0)
    ]

    loaded_layers = [] #empty list currently to hold the processed background images, did it individually before and it was rlly slow
    #so for every file(filename -> "Sky.png") and factor(the speed at which the image will move basically)

    for filename, factor in bg_layers:
        img = pygame.image.load(filename).convert_alpha() #loads the image with that name as a png and transpaernt
        w, h = img.get_size() #gets the size of the image and then stores them in variables for width and height
        """
        resizes images: pygame.transform.scale(surface, (new_width, new_height))
        so the new width is = int(w * scale_factor) which is just the integer version of the original times the scale i want
        same for the height
        """
        img = pygame.transform.scale(img, (int(w * SCALE_FACTOR), int(h * SCALE_FACTOR)))
        # adding the updated images to the empty tuple made earlier! could be done with a list or dictionary
        #but done with tuple cause the structure wont be updated or anything
        loaded_layers.append((img, factor))
    return loaded_layers
