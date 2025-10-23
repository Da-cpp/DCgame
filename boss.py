import pygame
import time
from utils import load_sound

class Boss:
    def __init__(self, x, y, idle_frames, glow_frames, attack_frames, death_frames, defense_frames, scale=3):
        
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
        self.attack_frames = scale_and_flip(attack_frames)
        self.death_frames = scale_and_flip(death_frames)
        self.defense_frames = scale_and_flip(defense_frames)

        #animation tracking
        self.idle_index = 0
        self.glow_index = 0
        self.attack_index = 0
        self.death_index = 0
        self.defense_index = 0 
        
        self.idle_timer = 0
        self.glow_timer = 0
        self.attack_timer = 0
        self.death_timer = 0
        self.defense_timer = 0
        
        self.idle_delay = 8
        self.glow_delay = 4
        self.attack_delay = 2 
        self.death_delay = 5
        self.defense_delay = 30
        
        #defense controls
        self.defense_duration_seconds = 6.0 
        self.defense_start_time = 0.0 
        
        #damage tracking for the defense
        self.damage_window_seconds = 1.0 
        self.damage_threshold = 45
        
        self.damage_log = [] 
        self.defense_cooldown_timer = 0 
        self.defense_cooldown_frames = 2 * 60 

        self.state = "idle"
        self.glowing = False
        self.attacking = False
        self.defending = False 
        self.dead = False
        self.scale = scale

        # health
        self.hp = 500
        self.max_hp = 500

        # glow distance tracking
        self.player_close_time = None
        self.glow_trigger_distance = 50


    def update(self, player):
        current_time = time.time()
        
        #clean old damage checks for defense
        cutoff_time = current_time - self.damage_window_seconds
        self.damage_log = [log for log in self.damage_log if log[0] >= cutoff_time]
        
        #check if dead first
        if self.hp <= 0:
            self.dead = True
            self.state = "death"

        if self.dead:
            #animate death and freeze on the last frame
            #put in sound too
            
            crunch = load_sound("crunch.wav", 0.8)
            if crunch: crunch.play()

            self.death_timer += 1
            if self.death_timer >= self.death_delay:
                self.death_timer = 0
                if self.death_index < len(self.death_frames) - 1:
                    self.death_index += 1
            return 
        
        
        #calc the health ratio
        health_ratio = self.hp / self.max_hp
        
       
        self.damage_threshold = 45 

        # adjust the threshold for  defense if health is low
        if health_ratio <= 0.3:
            #boss is below 30% hp, make defense EASIER MUHAHAHAHA
            
            self.damage_threshold = 35  


        # DEFENSE STATE MANAGEMENTS
        if self.defending:
            self.state = "defense"
            
            #defense lasts for 8 seconds
            if current_time - self.defense_start_time >= self.defense_duration_seconds:
                self.defending = False
                self.defense_cooldown_timer = self.defense_cooldown_frames
                self.state = "idle"
                
        elif self.defense_cooldown_timer > 0:
            #decrease the cooldown timer
            self.defense_cooldown_timer -= 1
            
        #defense trigger check
        elif not self.attacking and not self.glowing and self.defense_cooldown_timer == 0:
            total_damage = sum(log[1] for log in self.damage_log)
            
            if total_damage >= self.damage_threshold:
                #TRIGGER THE DEFENSE!!!! RELEASE THE ARMSSS1!!1
                self.defending = True
                self.defense_start_time = current_time
                self.defense_index = len(self.defense_frames) - 2 
                self.defense_timer = 0
                self.state = "defense"
                self.glowing = False
                self.attacking = False
                
                #boss heals during defense too, who's breaking through that
                self.heal(15) 

        #distance to player for glow trigger(only if not defending cause frames are diff)
        if not self.defending:
            boss_center_x = self.x + self.idle_frames[0].get_width() // 2
            distance = abs(player.x - boss_center_x)
            
            if distance <= self.glow_trigger_distance:
                if self.player_close_time is None:
                    self.player_close_time = current_time
                elif current_time - self.player_close_time >= 0.5 and not self.glowing and not self.attacking:
                    self.glowing = True
                    self.state = "glow"
                    self.glow_index = 0
                    self.glow_timer = 0
            else:
                self.player_close_time = None

        #handle animations
        if self.state == "idle":
            self.idle_timer += 1
            if self.idle_timer >= self.idle_delay:
                self.idle_timer = 0
                self.idle_index = (self.idle_index + 1) % len(self.idle_frames)

        elif self.state == "glow":
            self.glow_timer += 1
            if self.glow_timer >= self.glow_delay:
                self.glow_timer = 0
                self.glow_index += 1
                if self.glow_index >= len(self.glow_frames):
                    self.glowing = False
                    self.state = "attack"
                    self.attacking = True
                    self.attack_index = 0
                    self.attack_timer = 0

        elif self.state == "attack":
            self.attack_timer += 1
            if self.attack_timer >= self.attack_delay:
                self.attack_timer = 0
                self.attack_index += 1
                
                #hit player on a specific frame
                if self.attack_index == 3:
                    player.take_damage(20)
                    
                    player.x -= 450
                    thump = load_sound("thump.wav", 0.7)
                    if thump: thump.play()

                    if player.hp < 0:
                        player.hp = 0
                        
                if self.attack_index >= len(self.attack_frames):
                    self.attacking = False
                    self.state = "idle"
                    self.attack_index = 0
                        
        ##defense animation
        elif self.state == "defense":
            start_index = len(self.defense_frames) - 2
            
            self.defense_timer += 1
            if self.defense_timer >= self.defense_delay:
                self.defense_timer = 0
                
                #alternate between the last two frames
                if self.defense_index == start_index:
                    self.defense_index = start_index + 1
                else:
                    self.defense_index = start_index


    def draw(self, screen, camera_x, camera_y, zoom):
        if self.dead:
            frame = self.death_frames[self.death_index]
        elif self.state == "glow":
            frame = self.glow_frames[self.glow_index]
        elif self.state == "attack":
            frame = self.attack_frames[self.attack_index]
        elif self.state == "defense":
            frame = self.defense_frames[self.defense_index]
        else:
            frame = self.idle_frames[self.idle_index]

        screen.blit(frame, ((self.x - camera_x) * zoom, (self.y - camera_y) * zoom))

    def draw_hitbox(self, screen, camera_x, camera_y, zoom):
        scale_factor = 0.37
        full_w = self.idle_frames[0].get_width() * zoom
        full_h = self.idle_frames[0].get_height() * zoom
        w = full_w * scale_factor
        h = full_h * scale_factor
        offset_x = (full_w - w - 83) / 2
        offset_y = (full_h - h - 110) / 2
        rect = pygame.Rect((self.x - camera_x) * zoom + offset_x, (self.y - camera_y) * zoom + offset_y, w, h)
        
        color = (255, 0, 0)
        if self.defending:
            color = (0, 255, 255)
            
        pygame.draw.rect(screen, color, rect, 2)

    def get_hitbox(self, zoom):
        scale_factor = 0.37
        full_w = self.idle_frames[0].get_width() * zoom
        full_h = self.idle_frames[0].get_height() * zoom
        w = full_w * scale_factor
        h = full_h * scale_factor
        offset_x = (full_w - w - 83) / 2
        offset_y = (full_h - h - 110) / 2
        return pygame.Rect((self.x) * zoom + offset_x, (self.y) * zoom + offset_y, w, h)

    def take_damage(self, amount):
        if self.dead or self.defending: 
            return
        
        hit_sound = load_sound("damage.wav", 0.7)
        if hit_sound: hit_sound.play()
        self.hp -= amount
        
        self.damage_log.append((time.time(), amount))
        
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
        heal = load_sound("Absorb.wav")
        if heal: heal.play()
        # print(f"Boss healed for {amount} HP! Current HP: {self.hp}")

    def reset(self):
        #reset the boss for new game round
        self.hp = self.max_hp
        self.dead = False
        self.death_index = 0
        self.death_timer = 0
        self.state = "idle"
        self.glowing = False
        self.attacking = False
        self.defending = False
        self.defense_cooldown_timer = 0
        self.damage_log.clear()
        self.x = 950
        self.y = 170