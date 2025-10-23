import pygame
from settings import GRAVITY, SPEED
from utils import load_sound


class Player:
    def __init__(self, x, y, idle_frames, run_frames, jump_frames, dust_frames,
                 attack_frames, walk_dust_frames, hurt_frames, death_frames, parry_frames):
        
        #positions
        self.x = x
        self.y = y
        self.y_velocity = 0
        self.ground_level = y

        #animation frames
        self.idle_frames = idle_frames
        self.run_frames = run_frames
        self.jump_frames = jump_frames
        self.dust_frames = dust_frames
        self.attack_frames = attack_frames
        self.walk_dust_frames = walk_dust_frames
        self.hurt_frames = hurt_frames 
        self.death_frames = death_frames 
        self.parry_frames = parry_frames

        #animation control
        self.state = "idle"
        self.prev_state = "idle"
        self.direction = "right"
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 4 # th default delay for idle/run
        self.current_frame = self.idle_frames[0] if self.idle_frames else pygame.Surface((32, 32), pygame.SRCALPHA)

        #jump system
        self.jump_count = 0
        self.can_double_jump = True

        # dust control
        self.dust_active = False
        self.dust_index = 0
        self.dust_timer = 0
        self.dust_delay = 3
        self.dust_pos = (0, 0)

        #attack control
        self.attacking = False          
        self.attack_timer = 0
        self.attack_cooldown = 8 
        self.attack_dust_active = False
        self.attack_dust_index = 0
        self.attack_dust_timer = 0
        self.attack_dust_delay = 2
        self.attack_boost = 0 

        # parrying controls
        self.parrying = False
        self.parry_timer = 0
        self.parry_duration = 10    
        self.parry_active_window = 3
        self.parry_active = False   
        
        self.parry_cooldown_time = 40  #cooldown after attempt
        self.parry_cooldown_timer = 0  #when the next parry is ready

        #health controls
        self.hp = 100
        self.max_hp = 100
        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 10

        #death controls
        self.dead = False
        self.should_die = False
        self.death_index = 0
        self.death_timer = 0
        self.death_delay = 5
        self.death_animation_done = False

    #input and movement
    def handle_input(self, keys, world_width):
        # block movement during dying, attacking or parryign
        if self.dead or self.should_die or self.attacking or self.parrying: 
            return False
        
        moving = False
        if keys[pygame.K_RIGHT] and self.x < world_width - 23:
            self.x += SPEED
            self.direction = "right"
            moving = True
        if keys[pygame.K_LEFT] and self.x > -8:
            self.x -= SPEED
            self.direction = "left"
            moving = True
        return moving

    def jump(self):
        #block jump during dying, attacking or parrying
        if self.dead or self.should_die or self.attacking or self.parrying:
            return
        if self.jump_count == 0:
            self.y_velocity = -18
            self.jump_count = 1
        elif self.jump_count == 1 and self.can_double_jump:
            self.y_velocity = -18
            self.jump_count = 2
            self.can_double_jump = False
            self.trigger_dust()

    #dust effects
    def trigger_dust(self):
        self.dust_active = True
        self.dust_index = 0
        self.dust_timer = 0
        self.dust_pos = (self.x, self.y + 5)

    def trigger_attack_dust(self):
        self.attack_dust_active = True
        self.attack_dust_index = 0
        self.attack_dust_timer = 0
        if self.direction == "right":
            self.attack_dust_pos = (self.x - 10, self.y + 8)
        else:
            self.attack_dust_pos = (self.x + 10, self.y + 8)

    # gravity ass per
    def apply_gravity(self):
        if self.dead:
            return
            
        self.y_velocity += GRAVITY
        self.y += self.y_velocity
        
        if self.y >= self.ground_level:
            self.y = self.ground_level
            self.y_velocity = 0
            
            if not self.should_die:
                self.jump_count = 0
                self.can_double_jump = True

            if self.should_die:
                self.dead = True
                self.death_index = 0
                self.death_timer = 0
                return

    # attacking

    def attack(self):
        if self.dead or self.should_die or self.attacking or self.parrying:
            return
        self.attacking = True
        self.attack_timer = 0
        self.frame_index = 0
        self.trigger_attack_dust()
        
        initial_boost = 8 
        
        if self.direction == "right":
            self.x += 25
            self.attack_boost = initial_boost 
        else:
            self.x -= 25
            self.attack_boost = -initial_boost 

    # parrying
    def parry(self):
        #cant parry when you're dead can you?
        if not self.dead and not self.attacking and self.parry_cooldown_timer <= 0:
            self.parry_active = True
            self.parrying = True
            self.parry_timer = 0 #resets the parry timer
            self.frame_index = 0
            #set the timer immediately when the parry starts
            self.parry_cooldown_timer = self.parry_cooldown_time #start the long cooldown

    #state updates
    def update_state(self, moving):
        if self.dead:
            self.state = "death"
            die = load_sound("death.wav", 0.1)
            if die: die.play()
            return
        
        if self.should_die:
            self.state = "jump"
            return
        
        if self.parrying: 
            self.state = "parry"
        elif self.attacking:
            self.state = "attack"
        elif self.y < self.ground_level:
            self.state = "jump"
        elif moving:
            self.state = "run"
        else:
            self.state = "idle"

        if self.state != self.prev_state:
            self.frame_index = 0
            self.frame_timer = 0
        self.prev_state = self.state

    #animation
    def animate(self):
        
        current_frame_delay = self.frame_delay 
        frames = self.idle_frames
        
        #death animation logic and stuff
        if self.dead:
            frames = self.death_frames
            if not frames:
                self.death_animation_done = True
                return

            final_index = len(frames) - 1
            if self.death_index < final_index:
                self.death_timer += 1
                if self.death_timer >= self.death_delay:
                    self.death_timer = 0
                    self.death_index += 1
            else:
                self.death_animation_done = True
            self.current_frame = frames[self.death_index]

            if self.direction == "left":
                self.current_frame = pygame.transform.flip(self.current_frame, True, False)
            return

        #animation for living
        if self.state == "idle":
            frames = self.idle_frames
        elif self.state == "run":
            frames = self.run_frames
        elif self.state == "jump":
            frames = self.jump_frames
        elif self.state == "attack":
            frames = self.attack_frames
            self.attack_timer += 1
            current_frame_delay = 2 
            
            #reset attacking state after animation cycle and cooldown
            if self.frame_index >= len(frames) - 1 and self.attack_timer > self.attack_cooldown:
                self.attacking = False
        
        elif self.state == "parry": 
            frames = self.parry_frames
            current_frame_delay = 2 
            
            #lock animation to the last frame after the duration is over
            if self.parry_timer >= self.parry_duration:
                self.frame_index = len(frames) - 1
        
        else:
            frames = self.idle_frames

        # General Frame Advancement Logic

        self.frame_timer += 1
        
        if self.frame_timer >= current_frame_delay:
            self.frame_timer = 0
            if frames and self.state not in ["death"]:
                #alow jump frames to animate too
                if self.state != "parry" or self.parry_timer < self.parry_duration:
                    if self.state == "jump":
                        if self.frame_index < len(frames) - 1:
                            self.frame_index += 1
                    else:
                        self.frame_index = (self.frame_index + 1) % len(frames)


        #set the current frame
        self.current_frame = frames[self.frame_index]
        if self.direction == "left":
            self.current_frame = pygame.transform.flip(self.current_frame, True, False)


    #udpating
    def update(self, keys, world_width):
        if self.dead:
            self.attacking = False
            self.parrying = False
            self.y_velocity = 0
            self.update_state(False)
            self.animate()
            return
            
        if self.should_die:
            moving = False
        else:
            moving = self.handle_input(keys, world_width)
            
        self.apply_gravity()

        #parry stuff again
        if self.parry_cooldown_timer > 0:
            self.parry_cooldown_timer -= 1
        
        if self.parrying:
            self.parry_timer += 1
            
            
            if self.parry_timer >= self.parry_active_window:
                 self.parry_active = False 
            
            #turn off the*Parry State after the full duration
            if self.parry_timer >= self.parry_duration:
                self.parrying = False
                self.parry_timer = 0 
       
        
        #attack movement
        if self.attacking:
            self.x += self.attack_boost
            self.attack_boost *= 0.7
        
            
        self.update_state(moving)
        self.animate()

        if self.is_hurt:
            self.hurt_timer += 1
            if self.hurt_timer >= self.hurt_duration:
                self.is_hurt = False
                self.hurt_timer = 0

    # drawing
    def draw(self, screen, camera_x, camera_y, zoom):
        #draw player sprite
        screen.blit(self.current_frame, ((self.x - camera_x) * zoom, (self.y - camera_y) * zoom))
            
        #draw dust effects
        self.animate_dust(screen, camera_x, camera_y, zoom)
        self.animate_attack_dust(screen, camera_x, camera_y, zoom)

    #dust animations  ---
    def animate_dust(self, screen, camera_x, camera_y, zoom):
       
        if not self.dust_active:
            return
        self.dust_timer += 1
        if self.dust_timer >= self.dust_delay:
            self.dust_timer = 0
            
            if self.dust_index < len(self.dust_frames):
                frame = self.dust_frames[self.dust_index]
                
                #draw logic
                scaled_x = (self.dust_pos[0] - camera_x) * zoom
                scaled_y = (self.dust_pos[1] - camera_y) * zoom
                screen.blit(frame, (scaled_x, scaled_y))
                
                self.dust_index += 1
            else:
                self.dust_active = False

    #what do you think?
    def animate_attack_dust(self, screen, camera_x, camera_y, zoom):
        
        if not self.attack_dust_active:
            return
        self.attack_dust_timer += 1
        if self.attack_dust_timer >= self.attack_dust_delay:
            self.attack_dust_timer = 0
            
            if self.attack_dust_index < len(self.walk_dust_frames):
                frame = self.walk_dust_frames[self.attack_dust_index]
                
                
                scaled_x = (self.attack_dust_pos[0] - camera_x) * zoom
                scaled_y = (self.attack_dust_pos[1] - camera_y) * zoom
                screen.blit(frame, (scaled_x, scaled_y))
                
                self.attack_dust_index += 1
            else:
                self.attack_dust_active = False
                
    #hitbox for debugging and stuff
    def draw_hitbox(self, screen, camera_x, camera_y, zoom):
        scale_factor = 0.66
        full_w = self.current_frame.get_width() * zoom
        full_h = self.current_frame.get_height() * zoom
        w = full_w * scale_factor
        h = full_h * scale_factor
        offset_x = (full_w - w - 9) / 2
        offset_y = (full_h - h) / 2
        rect = pygame.Rect((self.x - camera_x) * zoom + offset_x, (self.y - camera_y) * zoom + offset_y, w, h)
        pygame.draw.rect(screen, (0, 255, 0), rect, 2) # Draw the green box

    def get_hitbox(self, zoom):
        scale_factor = 0.66
        full_w = self.current_frame.get_width() * zoom
        full_h = self.current_frame.get_height() * zoom
        w = full_w * scale_factor
        h = full_h * scale_factor
        offset_x = (full_w - w - 9) / 2
        offset_y = (full_h - h) / 2
        #returns the actual rect object for collision checking (using world coordinates and not thescreen coordinates)
        return pygame.Rect((self.x) * zoom + offset_x, (self.y) * zoom + offset_y, w, h)

    #health
    def take_damage(self, amount):
        if self.dead or self.should_die or self.is_hurt: #is hurtfor temporary invincibility
            return
        self.hp -= amount
        
        if self.hp <= 0:
            self.hp = 0
            self.should_die = True
            self.death_index = 0
            self.death_timer = 0
            self.is_hurt = False 
            self.hurt_timer = 0
            
        if not self.should_die:
            self.is_hurt = True
            self.hurt_timer = 0
    #healinggg
    def heal(self, amount):
        
        if self.dead or self.should_die:
            return
        self.hp += amount
        heal = load_sound("Heal.wav", 0.7)
        if heal: heal.play()
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def respawn(self, x, y):
        self.x = x
        self.y = y
        self.y_velocity = 0
        self.hp = 100
        self.should_die = False
        self.dead = False
        self.death_index = 0
        self.death_timer = 0
        self.death_animation_done = False
        self.state = "idle"
        self.jump_count = 0
        self.can_double_jump = True