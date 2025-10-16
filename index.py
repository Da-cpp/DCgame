import os
import pygame
from sys import exit
from background import load_background_layers
from sprites import load_sprites
from settings import ZOOM, GRAVITY, SPEED, FPS
# from enemy import Enemy
from sprites import load_sprites, load_boss_sprites
from boss import Boss


#centering the window so it doesn't spawn offscreen
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

# Load assets
loaded_layers = load_background_layers()
idle_frames, run_frames, jump_frames, dust_frames = load_sprites()
boss_idle_frames, boss_glow_frames = load_boss_sprites()

boss = Boss(x=950, y=170, idle_frames=boss_idle_frames, glow_frames=boss_glow_frames, scale=3)


#enemy stuff
# enemy_walk, enemy_attack = load_enemy_sprites()
# enemy = Enemy(10, 389, enemy_walk, enemy_attack)  # starting position

#screen size based on largest layer(all are the same size rn but incase i need to add another)
SCREEN_WIDTH, SCREEN_HEIGHT = loaded_layers[0][0].get_size()
#makes the screen at this size!

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dax Sprite")

#sprite spawning stuff and sprite attributes etc
x = SCREEN_WIDTH // 2 - 16
y = 389
y_velocity = 0
ground_level = y

#animation states
frame_index = 0
frame_timer = 0
frame_delay = 4 #faster animation
state = "idle"
prev_state = state
direction = "right"

#double jump stuff
jump_count = 0
can_double_jump = True

#dust animation controlling
dust_active = False
dust_index = 0
dust_timer = 0
dust_delay = 3
dust_pos = (0, 0)

zoomed_layers = [(pygame.transform.rotozoom(img, 0, ZOOM), factor) for img, factor in loaded_layers]
clock = pygame.time.Clock()

#main loop
while True:
    moving = False

    #the events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        #keydown things for the jump and double jump
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if jump_count == 0: #the first jump
                    y_velocity = -18 # was -15 changed for higher jump
                    jump_count = 1
                elif jump_count == 1 and can_double_jump: #the second jump
                    y_velocity = -18
                    jump_count = 2
                    can_double_jump = False

                    #dust triggers
                    dust_active = True
                    dust_index = 0
                    dust_timer = 0
                    dust_pos = (x, y + 5)


    
    keys = pygame.key.get_pressed()
    base_bg = loaded_layers[0][0]
    world_width = base_bg.get_width()
    #key for moving left or right
    if keys[pygame.K_RIGHT] and x < world_width - 23:
        x += SPEED
        direction = "right"
        moving = True
    if keys[pygame.K_LEFT] and x > -8:
        x -= SPEED
        direction = "left"
        moving = True

    #gravity
    y_velocity += GRAVITY
    y += y_velocity
    #ground collissions 
    if y >= ground_level:
        y = ground_level
        y_velocity = 0
        jump_count = 0
        can_double_jump = True

    #my state stuff, if y is less than the set ground level then he's jumping
    if y < ground_level:
        state = "jump"
    elif moving:
        state = "run"
    else:
        state = "idle"

    #reset animation!
    if state != prev_state:
        frame_index = 0
        frame_timer = 0
    prev_state = state

    #selects the frames
    if state == "idle":
        frames = idle_frames
    elif state == "run":
        frames = run_frames
    else:
        frames = jump_frames

    #animating
    frame_timer += 1
    if frame_timer >= frame_delay:
        frame_timer = 0
        frame_index = (frame_index + 1) % len(frames)
    current_frame = frames[frame_index]
    #flip the sprite if moving left
    if direction == "left":
        current_frame = pygame.transform.flip(current_frame, True, False)

    #camera following!!
    camera_x = x - SCREEN_WIDTH / (2 * ZOOM)
    camera_y = y - SCREEN_HEIGHT / (2 * ZOOM)

    #clamping the  camera so it doesnt go out of bounds
    base_bg = loaded_layers[0][0]
    zoomed_width = base_bg.get_width() * ZOOM
    zoomed_height = base_bg.get_height() * ZOOM
    max_camera_x = max(0, zoomed_width - SCREEN_WIDTH)
    max_camera_y = max(0, zoomed_height - SCREEN_HEIGHT)
    camera_x = max(0, min(camera_x, max_camera_x / ZOOM))
    camera_y = max(0, min(camera_y, max_camera_y / ZOOM))

    #drawing the background!
    screen.fill((0, 0, 0))
    for img, factor in zoomed_layers:
        offset_x = -camera_x * factor
        offset_y = -camera_y * factor
        screen.blit(img, (offset_x, offset_y))

    #drawing the sprite
    screen.blit(current_frame, ((x - camera_x) * ZOOM, (y - camera_y) * ZOOM))

    #drawing the double jump dust!
    if dust_active:
        dust_timer += 1
        if dust_timer >= dust_delay:
            dust_timer = 0
            if dust_index < len(dust_frames):
                frame = dust_frames[dust_index]
                screen.blit(frame, ((dust_pos[0] - camera_x) * ZOOM, (dust_pos[1] - camera_y) * ZOOM))
                dust_index += 1
            else:
                dust_active = False

    # enemy.update(x, y)
    # screen.blit(enemy.get_frame(), ((enemy.x - camera_x) * ZOOM, (enemy.y - camera_y) * ZOOM))
    boss.update(x, y)
    boss.draw(screen, camera_x, camera_y, ZOOM)

     

    pygame.display.flip()
    clock.tick(FPS)

    #GOT LAZY WITH COMMENTING, WILL FIX UP AND CODE MORE TMR(DID NOT FIX UP TMR)