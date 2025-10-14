import pygame
from sys import exit

pygame.init()

# loading the background and getting the size of it
bg = pygame.image.load("7.png")
SCREEN_WIDTH, SCREEN_HEIGHT = bg.get_size()

# Set display
screen = pygame.display.set_mode((SCREEN_WIDTH*2, SCREEN_HEIGHT*2))
pygame.display.set_caption("Dax Sprite")

# Scale background
bg = pygame.transform.scale(bg, (SCREEN_WIDTH*2, SCREEN_HEIGHT*2)).convert()

# Helper function to extract frames with transparency
def get_frames(sheet, num_frames, width, height, scale=1):
    frames = []
    for i in range(num_frames):
        frame = pygame.Surface((width, height), pygame.SRCALPHA)  # transparent surface
        frame.blit(sheet, (0,0), (i*width, 0, width, height))
        frame = pygame.transform.scale(frame, (width*scale, height*scale))
        frames.append(frame)
    return frames

# Load sprite sheets
idle_sheet_img = pygame.image.load("Pink_Monster_Idle_4.png").convert_alpha()
run_sheet_img  = pygame.image.load("Pink_Monster_Run_6.png").convert_alpha()
jump_sheet_img = pygame.image.load("Pink_Monster_Jump_8.png").convert_alpha()

# Extract frames using transparent logic
idle_frames = get_frames(idle_sheet_img, 4, 32, 32, 1)
run_frames  = get_frames(run_sheet_img, 6, 32, 32, 1)
jump_frames = get_frames(jump_sheet_img, 8, 32, 32, 1)

# Character properties
x, y = 500, 500
y_velocity = 0
gravity = 1
ground_level = y
speed = 5

# Animation control
frame_index = 0
frame_timer = 0
frame_delay = 5

state = "idle"  # "idle", "run", "jump"
prev_state = state
direction = "right"  # "right" or "left"
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Key input
    keys = pygame.key.get_pressed()
    moving = False

    # Horizontal movement
    if keys[pygame.K_RIGHT]:
        x += speed
        direction = "right"
        moving = True
    if keys[pygame.K_LEFT]:
        x -= speed
        direction = "left"
        moving = True

    # Jumping
    if keys[pygame.K_UP] and y == ground_level:
        y_velocity = -15  # jump strength

    # Determine state
    if y < ground_level:  # in the air
        state = "jump"
    elif moving:
        state = "run"
    else:
        state = "idle"

    # Apply gravity
    y_velocity += gravity
    y += y_velocity
    if y >= ground_level:
        y = ground_level
        y_velocity = 0

    # Reset frame index if state changed
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


# import pygame
# from sys import exit

# pygame.init()

# class SpriteSheet():
#     def __init__(self, image):
#         self.sheet = image
    
#     def get_image(self, frame, width, height, scale):
#         # Create a fully transparent surface
#         image = pygame.Surface((width, height), pygame.SRCALPHA)
#         image.fill((0, 0, 0, 0))
#         # Copy the frame from the sprite sheet
#         image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))
#         # Scale while keeping transparency
#         image = pygame.transform.scale(image, (width*scale, height*scale))
#         return image

