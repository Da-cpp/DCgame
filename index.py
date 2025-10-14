import pygame
from sys import exit

pygame.init()

# loading the background and getting the size of it
bg = pygame.image.load("7.png")
SCREEN_WIDTH, SCREEN_HEIGHT = bg.get_size()

# set the display at twice the images size
screen = pygame.display.set_mode((SCREEN_WIDTH*2, SCREEN_HEIGHT*2))
pygame.display.set_caption("Dax Sprite")

# scaling it to twice the images size
bg = pygame.transform.scale(bg, (SCREEN_WIDTH*2, SCREEN_HEIGHT*2)).convert()

# extracts the frames with transparancy instead of just filling in with black
def get_frames(sheet, num_frames, width, height, scale=1):
    frames = []
    for i in range(num_frames):
        frame = pygame.Surface((width, height), pygame.SRCALPHA)  # transparent surface now
        frame.blit(sheet, (0,0), (i*width, 0, width, height))
        frame = pygame.transform.scale(frame, (width*scale, height*scale))
        frames.append(frame)
    return frames

# load all sprite sheets
idle_sheet_img = pygame.image.load("Pink_Monster_Idle_4.png").convert_alpha()
run_sheet_img  = pygame.image.load("Pink_Monster_Run_6.png").convert_alpha()
jump_sheet_img = pygame.image.load("Pink_Monster_Jump_8.png").convert_alpha()

# extracting the frames using how many of them there are and each size
idle_frames = get_frames(idle_sheet_img, 4, 32, 32, 1)
run_frames  = get_frames(run_sheet_img, 6, 32, 32, 1)
jump_frames = get_frames(jump_sheet_img, 8, 32, 32, 1)

#properties
x, y = 500, 500
y_velocity = 0
gravity = 1
ground_level = y
speed = 5

#animation and stuff
frame_index = 0
frame_timer = 0
frame_delay = 5


state = "idle"  # different states are: "idle", "run", "jump"
# needs to record previous state
prev_state = state
direction = "right"  #different directions seeing as the sprite will need to b flipped "right" or "left"
#makes sure it doesnt run too fast
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # which key was pressed input
    keys = pygame.key.get_pressed()
    #sprite is automatically still and therefore "idle"
    moving = False

    #moving left & right
    if keys[pygame.K_RIGHT]:
        x += speed
        direction = "right"
        moving = True
    if keys[pygame.K_LEFT]:
        x -= speed
        direction = "left"
        moving = True

    #jumps
    if keys[pygame.K_UP] and y == ground_level:
        y_velocity = -15  # how high this mf can jump

    # checks the state
    if y < ground_level:  #means he's in the air
        state = "jump"
    elif moving:
        state = "run"
    else:
        state = "idle"

    #gravity so he comes back down
    y_velocity += gravity
    y += y_velocity
    if y >= ground_level:
        y = ground_level
        y_velocity = 0

    #if state is changed will reset
    if state != prev_state:
        frame_index = 0
        frame_timer = 0
    prev_state = state

    # Select frames based on state
    if state == "idle":
        frames = idle_frames
    elif state == "run":
        frames = run_frames
    elif state == "jump":
        frames = jump_frames

    # Animate
    frame_timer += 1
    if frame_timer >= frame_delay:
        frame_timer = 0
        frame_index = (frame_index + 1) % len(frames)

    current_frame = frames[frame_index]

    # Flip sprite if moving left
    if direction == "left":
        current_frame = pygame.transform.flip(current_frame, True, False)

    # Draw background and sprite
    screen.blit(bg, (0, 0))
    screen.blit(current_frame, (x, y))

    pygame.display.flip()
    clock.tick(60)
