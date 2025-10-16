import pygame

# function to extract the frames from the spritesheet
def get_frames(sheet, num_frames, width, height):
    frames = [] #empty list so it'll store each frame separately 

    for i in range(num_frames):
        #creates nw surface for the frame and then makes it transparent
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        #draws unto surface based on each frame on the sheet, eg frame one starts at i(0)* width(32)
        #then frame 2 would start at i(1)* width(32)
        frame.blit(sheet, (0, 0), (i * width, 0, width, height))
        #adds to frame list!
        frames.append(frame)
    return frames

def load_sprites():
    #load sprite sheets
    idle = pygame.image.load("Pink_Monster_Idle_4.png").convert_alpha()
    run = pygame.image.load("Pink_Monster_Run_6.png").convert_alpha()
    jump = pygame.image.load("Pink_Monster_Jump_8.png").convert_alpha()
    dust = pygame.image.load("Double_Jump_Dust_5.png").convert_alpha()

    #extract the frames based on how many frames there are etc
    idle_frames = get_frames(idle, 4, 32, 32)
    run_frames = get_frames(run, 6, 32, 32)
    jump_frames = get_frames(jump, 8, 32, 32)
    dust_frames = get_frames(dust, 5, 32, 32)

    return idle_frames, run_frames, jump_frames, dust_frames

#loads the boss in
def load_boss_sprites():
    #diff spritesheets for the boss in transparent
    boss_idle = pygame.image.load("Golem_Idle_4.png").convert_alpha()
    boss_glow = pygame.image.load("Golem_Glow_8.png").convert_alpha()

    #extracting the frames
    boss_idle_frames = get_frames(boss_idle, 4, 100, 100)
    boss_glow_frames = get_frames(boss_glow, 8, 100, 100)

    return boss_idle_frames, boss_glow_frames


