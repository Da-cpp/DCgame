import pygame
import time

#boss class for the attacking boss
class Boss:
    def __init__(self, x, y, idle_frames, glow_frames, scale=3, glow_trigger_distance=300, glow_cooldown=2):
        def scale_and_flip(frames):
            out = []
            for f in frames:
                f2 = pygame.transform.scale(f, (f.get_width() * scale, f.get_height() * scale))
                f2 = pygame.transform.flip(f2, True, False)
                out.append(f2)
            return out

        self.x = x
        self.y = y
        self.idle_frames = scale_and_flip(idle_frames)
        self.glow_frames = scale_and_flip(glow_frames)

        #animation tracking
        self.idle_index = 0
        self.glow_index = 0
        self.idle_timer = 0
        self.glow_timer = 0
        self.idle_delay = 8
        self.glow_delay = 4

        self.state = "idle"
        self.glowing = False

        #distance and the cooldown settings
        self.glow_trigger_distance = glow_trigger_distance
        self.glow_cooldown = glow_cooldown
        self.last_glow_time = 0  #teh time since last glow

    def update(self, player_x, player_y):
        #get boss center x position
        boss_center_x = self.x + self.idle_frames[0].get_width() // 2
        distance_x = abs(player_x - boss_center_x)

        #check if close enough and the cooldown has passed
        current_time = time.time()
        can_trigger = (current_time - self.last_glow_time) > self.glow_cooldown

        if distance_x < self.glow_trigger_distance and not self.glowing and can_trigger:
            self.glowing = True
            self.state = "glow"
            self.glow_index = 0
            self.glow_timer = 0
            self.last_glow_time = current_time

        #idle animation
        if self.state == "idle":
            self.idle_timer += 1
            if self.idle_timer >= self.idle_delay:
                self.idle_timer = 0
                self.idle_index = (self.idle_index + 1) % len(self.idle_frames)

        #glow animation
        elif self.state == "glow":
            self.glow_timer += 1
            if self.glow_timer >= self.glow_delay:
                self.glow_timer = 0
                self.glow_index += 1
                if self.glow_index >= len(self.glow_frames):
                    #finish glow and then return to the idle ani
                    self.glowing = False
                    self.state = "idle"
                    self.glow_index = 0
                    self.glow_timer = 0

    def draw(self, screen, camera_x, camera_y, zoom):
        #draw glow if active
        if self.state == "glow":
            glow_frame = self.glow_frames[self.glow_index]
            screen.blit(glow_frame, ((self.x - camera_x) * zoom, (self.y - camera_y) * zoom))
        else:
            #only draw idle when not glowing
            frame = self.idle_frames[self.idle_index]
            screen.blit(frame, ((self.x - camera_x) * zoom, (self.y - camera_y) * zoom))
