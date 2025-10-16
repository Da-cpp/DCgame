import pygame

def update_camera(camera_x, camera_y, zoom, loaded_layers, screen_width, screen_height):
    #keeps the camera within world boundaries.
    base_bg = loaded_layers[0][0]  # Base/background layer
    zoomed_width = base_bg.get_width() * zoom
    zoomed_height = base_bg.get_height() * zoom

    #calculate max scroll distance
    max_camera_x = max(0, zoomed_width - screen_width)
    max_camera_y = max(0, zoomed_height - screen_height)

    #clamp camera position
    camera_x = max(0, min(camera_x, max_camera_x / zoom))
    camera_y = max(0, min(camera_y, max_camera_y / zoom))

    return camera_x, camera_y


def apply_zoom(loaded_layers, zoom):
    #return zoomed versions of each parallax layer.
    zoomed_layers = []
    for img, factor in loaded_layers:
        width = int(img.get_width() * zoom)
        height = int(img.get_height() * zoom)
        scaled_img = pygame.transform.scale(img, (width, height))
        zoomed_layers.append((scaled_img, factor))
    return zoomed_layers
