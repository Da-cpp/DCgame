import os
import pygame
from sys import exit
import random 
from background import load_background_layers
from sprites import load_sprites, load_boss_sprites 
from settings import ZOOM, GRAVITY, SPEED, FPS
from boss import Boss
from projectile import Projectile
from player import Player
from heal import HealingItem 
from utils import resource_path, load_sound, play_music


#center the window for launch
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
#for sound
pygame.mixer.init(frequency=44100, size=-16, channels=6, buffer=512)

play_music("DnB_1.wav", volume=0.2)
amount=0.2

#
#LOAD ASSETS AND INITIALIZATION
idle_frames, run_frames, jump_frames, dust_frames, attack_frames, walk_dust_frames, hurt_frames, death_frames, parry_frames = load_sprites() 
boss_idle_frames, boss_glow_frames, boss_attack_frames, boss_death_frames, boss_defense_frames = load_boss_sprites()

#load the healing items images
HEALING_ITEM_IMAGES = HealingItem.load_item_images() 

#create boss instance
boss = Boss(950, 170, boss_idle_frames, boss_glow_frames, boss_attack_frames, boss_death_frames, boss_defense_frames, scale=3)

# setup display
loaded_layers = load_background_layers()
SCREEN_WIDTH, SCREEN_HEIGHT = loaded_layers[0][0].get_size()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dax Sprite")

# projectile setup
projectiles = pygame.sprite.Group() # Group for active projectiles
PROJECTILE_SPAWN_RATE = 40
projectile_spawn_timer = PROJECTILE_SPAWN_RATE

WORLD_GROUND_LEVEL = 363 
PROJECTILE_Y_MIN = 200
PROJECTILE_Y_MAX = WORLD_GROUND_LEVEL
PROJECTILE_SCALE = 1

WORLD_WIDTH = loaded_layers[0][0].get_width()

#initialize player
player = Player(SCREEN_WIDTH // 2 - 16, WORLD_GROUND_LEVEL,
                idle_frames, run_frames, jump_frames,
                dust_frames, attack_frames, walk_dust_frames, hurt_frames, death_frames,
                parry_frames)

game_state = "play"

#prepare the background layers with zoom
zoomed_layers = [(pygame.transform.rotozoom(img, 0, ZOOM), factor) for img, factor in loaded_layers]
clock = pygame.time.Clock()

#healing item stuff
SPAWN_INTERVAL = 10 * FPS
spawn_timer = SPAWN_INTERVAL
current_healing_item = None
MIN_SPAWN_X = 50 
MAX_SPAWN_X = loaded_layers[0][0].get_width() - 50 


#health bar

def draw_fancy_health_bar(screen, x, y, width, height, current_hp, max_hp, is_player=False):
    # his function draws the health bar
    BORDER_COLOR = (40, 40, 40)
    SHADOW_COLOR = (10, 10, 10)
    health_ratio = current_hp / max_hp
    current_width = int(width * health_ratio)
    #colour vs health
    if health_ratio > 0.6:
        HEALTH_COLOR = (0, 200, 0)
    elif health_ratio > 0.25:
        HEALTH_COLOR = (255, 200, 0)
    else:
        HEALTH_COLOR = (255, 0, 0)

    #drawnig the actual bars
    pygame.draw.rect(screen, BORDER_COLOR, (x, y, width, height), 0, 3)
    pygame.draw.rect(screen, SHADOW_COLOR, (x + 1, y + 1, width - 2, height - 2), 0, 2)

    #width is based on health so if the health is greater than zero draw
    if current_width > 0:
        bar_rect = pygame.Rect(x + 2, y + 3, current_width - 4, height - 6)
        pygame.draw.rect(screen, HEALTH_COLOR, bar_rect, 0, 1)
        highlight_height = max(1, (height - 6) // 4)
        highlight_rect = pygame.Rect(x + 2, y + 3, current_width - 4, highlight_height)
        pygame.draw.rect(screen, (255, 255, 255, 50), highlight_rect, 0, 1)

    #if this is the player's bar then put the amount
    if is_player:
        font = pygame.font.Font(None, 18)
        text = font.render(f"{int(current_hp)}/{int(max_hp)}", True, (255, 255, 255))
        screen.blit(text, (x + width // 2 - text.get_width() // 2, y + height // 2 - text.get_height() // 2))


#main thing
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and game_state == "play":
            if event.key == pygame.K_UP:
                player.jump()
                jump = load_sound("jump.wav", 0.1)
                if jump: jump.play()
                
            if event.key == pygame.K_z:
                player.attack()
            if event.key == pygame.K_x:
                player.parry()

   #playing
    if game_state == "play":
        keys = pygame.key.get_pressed()
        
        boss_health_ratio = boss.hp / boss.max_hp
        
        #player center for the targetting arms
        player_center_x = player.x + (player.current_frame.get_width() / 2)
        player_center_y = player.y + (player.current_frame.get_height() / 2)

        #basically boss phases
        current_proj_rate = PROJECTILE_SPAWN_RATE
        current_proj_speed = 5
        projectile_type_chance = 0 

        if boss_health_ratio <= 0.6 and boss_health_ratio > 0.3:
            # phase 2, 60% - 30% hp
            current_proj_rate = 28 
            current_proj_speed = 7
            projectile_type_chance = 40 

        elif boss_health_ratio <= 0.3:
            # phase 3, < 30% hp (bullet hell)(turned down cause it was crazy hard)
            
            current_proj_rate = 18 
            current_proj_speed = 7
            projectile_type_chance = 60 
            
            
        #spawn healing items(projectiles, just changed names and stuff to remember it can heal now)
        if current_healing_item is None:
            spawn_timer -= 1
            if spawn_timer <= 0:
                item_name = random.choice(list(HealingItem.HEAL_VALUES.keys()))
                current_healing_item = HealingItem(item_name, HEALING_ITEM_IMAGES, WORLD_GROUND_LEVEL, MIN_SPAWN_X, MAX_SPAWN_X)
                spawn_timer = SPAWN_INTERVAL
                current_healing_item.boss_steal_timer = 5 * FPS 

        # update player
        player.update(keys, WORLD_WIDTH)

        #player hitting boss
        if player.attacking:
            player_hitbox = player.get_hitbox(ZOOM)
            boss_hitbox = boss.get_hitbox(ZOOM)
            if player_hitbox.colliderect(boss_hitbox):
                boss.take_damage(2)
                
        #update boss
        boss.update(player)

        # death and win checks
        if player.hp <= 0 and not player.dead:
            player.should_die = True
        elif player.dead and player.death_animation_done:
            game_state = "respawn_menu"

        if boss.dead and boss.death_index == len(boss.death_frames) - 1:
            
            game_state = "win"

        # boss projectiles 
        if boss.defending:
            projectile_spawn_timer -= 1
            if projectile_spawn_timer <= 0:
                
                #projectile type and the randomness of it all
                proj_type = "straight"
                if random.randint(1, 100) <= projectile_type_chance:
                    proj_type = random.choice(["jumping", "targeted"])
                #spawninggg
                launch = load_sound("launch.wav", 0.7)
                if launch: launch.play()
                
                projectiles.add(Projectile(WORLD_WIDTH, PROJECTILE_Y_MIN, PROJECTILE_Y_MAX, 
                                            speed=current_proj_speed, scale=PROJECTILE_SCALE, 
                                            type=proj_type, target_pos=(player_center_x, player_center_y)))
                projectile_spawn_timer = current_proj_rate

        #update all projectiles
        projectiles.update()

        #PROJECTILE COLLISION AN PARRY LOGIC
        
        #calculate players hitbox once per frame
        player_hitbox = player.get_hitbox(ZOOM) 
        
        #list to hold projectiles that need removal (offscreen or parried)
        hit_or_removed_projectiles = [] 

        #projectile hitbox
        for proj in projectiles.copy(): 
            proj_hitbox = proj.get_hitbox(ZOOM)
            
            #check for offscreen remove
            if proj.is_off_screen(WORLD_WIDTH): 
                hit_or_removed_projectiles.append(proj)
                continue
                
            #check for successful parry
            if player.parry_active:
                if player_hitbox.colliderect(proj_hitbox):
                    #SUCCESSFUL PARRY!!!!!!!!!!!
                    player.heal(5) 
                    print("Parry successful! +5 HP")
                    hit_or_removed_projectiles.append(proj)
                    continue
            
            #check for normal player damage (only if the player is not in the parrying state)
            elif not player.parrying: 
                if player_hitbox.colliderect(proj_hitbox):
                    
                    player.take_damage(proj.damage)
                    hit_or_removed_projectiles.append(proj)
                    continue 

        #take off the projectiles that were parried/off-screen
        projectiles.remove(*hit_or_removed_projectiles) 

       #BOSS HEAL WITH POTION 
        if current_healing_item:
            current_healing_item.update()
            item_hitbox = current_healing_item.get_hitbox(ZOOM)
            
            #steal timer
            if not current_healing_item.is_stolen:
                current_healing_item.boss_steal_timer -= 1
            
            boss_hitbox = boss.get_hitbox(ZOOM)
            
            #trigger boss stealing
            if current_healing_item.boss_steal_timer <= 0 and not current_healing_item.is_stolen:
                current_healing_item.is_stolen = True
                current_healing_item.target = boss
                # print("Boss is pulling item")

            #check if boss touched it
            if current_healing_item.is_stolen and boss_hitbox.colliderect(item_hitbox):
                #BOSS HEALS
                boss.heal(current_healing_item.heal_amount)
                current_healing_item = None
                spawn_timer = SPAWN_INTERVAL
                
            elif not current_healing_item.is_stolen and player_hitbox.colliderect(item_hitbox):
                #PLAYER HEALS
                player.heal(current_healing_item.heal_amount)
                current_healing_item = None
                spawn_timer = SPAWN_INTERVAL
                
        #camera calcs
        camera_x = player.x - SCREEN_WIDTH / (2 * ZOOM)
        camera_y = player.y - SCREEN_HEIGHT / (2 * ZOOM)
        zoomed_width = WORLD_WIDTH * ZOOM 
        zoomed_height = loaded_layers[0][0].get_height() * ZOOM
        camera_x = max(0, min(camera_x, (zoomed_width - SCREEN_WIDTH) / ZOOM))
        camera_y = max(0, min(camera_y, (zoomed_height - SCREEN_HEIGHT) / ZOOM))

        #draw world
        screen.fill((0, 0, 0))
        for img, factor in zoomed_layers:
            #parallax stuff again
            screen.blit(img, (-camera_x * factor * ZOOM, -camera_y * factor * ZOOM))

        # draw sprites
        boss.draw(screen, camera_x, camera_y, ZOOM)
        player.draw(screen, camera_x, camera_y, ZOOM)
        if current_healing_item:
            current_healing_item.draw(screen, camera_x, camera_y, ZOOM)
            
        # draw projectiles using the group's draw method
        for p in projectiles:
            p.draw(screen, camera_x, camera_y, ZOOM)

        # draw health bars 
        BAR_WIDTH, BAR_HEIGHT, MARGIN = 200, 25, 20
        draw_fancy_health_bar(screen, MARGIN, MARGIN, BAR_WIDTH, BAR_HEIGHT, player.hp, player.max_hp, is_player=True)
        draw_fancy_health_bar(screen, SCREEN_WIDTH - MARGIN - BAR_WIDTH, MARGIN, BAR_WIDTH, BAR_HEIGHT, boss.hp, boss.max_hp)
        
    #MENUSSS
    elif game_state in ["respawn_menu", "win"]:
        #semi transparent overlay so it isnt bland
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        #text title which has a shadow
        title_text = "You Died" if game_state == "respawn_menu" else "You Won!"
        title_color = (255, 50, 50) if game_state == "respawn_menu" else (255, 230, 100) 
        
        font = pygame.font.Font(None, 80) 
        
        #show text/render
        text_to_render = font.render(title_text, True, title_color)
        text_rect = text_to_render.get_rect(center=(SCREEN_WIDTH // 2, 150))

        #draw the shadow
        shadow_color = (0, 0, 0)
        shadow_offset = 4 
        shadow_text = font.render(title_text, True, shadow_color)
        screen.blit(shadow_text, text_rect.move(shadow_offset, shadow_offset))

        # draw main text
        screen.blit(text_to_render, text_rect)

        #buttons with hover effect
        button_font = pygame.font.Font(None, 40)
        main_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 260, 200, 60)
        quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 360, 200, 60)

        #mouse posistion for the hovers
        mouse_pos = pygame.mouse.get_pos()
        main_hover = main_button.collidepoint(mouse_pos)
        quit_hover = quit_button.collidepoint(mouse_pos)
        
        #colours for hover
        main_label = "Respawn" if game_state == "respawn_menu" else "Play Again"
        main_color = (100, 200, 100) if main_hover else (50, 150, 50) 
        quit_color = (200, 100, 100) if quit_hover else (150, 50, 50) 

        pygame.draw.rect(screen, main_color, main_button, border_radius=10)
        pygame.draw.rect(screen, quit_color, quit_button, border_radius=10)

        #drw the button text
        main_text_surface = button_font.render(main_label, True, (255, 255, 255))
        quit_text_surface = button_font.render("Quit", True, (255, 255, 255))
        
        screen.blit(main_text_surface, main_text_surface.get_rect(center=main_button.center))
        screen.blit(quit_text_surface, quit_text_surface.get_rect(center=quit_button.center))

        pygame.display.flip()

        waiting = True
        while waiting:
            #events for the menu while 'waiting' in the menu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if main_button.collidepoint(event.pos):
                        player.respawn(SCREEN_WIDTH // 2 - 16, WORLD_GROUND_LEVEL) # Use correct respawn location
                        if game_state == "win":
                            boss.reset() 
                        game_state = "play"
                        waiting = False
                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        exit()
                
                #redraws menu according the mouse position and hover
                mouse_pos = pygame.mouse.get_pos()
                main_hover = main_button.collidepoint(mouse_pos)
                quit_hover = quit_button.collidepoint(mouse_pos)
                
                main_color = (100, 200, 100) if main_hover else (50, 150, 50) 
                quit_color = (200, 100, 100) if quit_hover else (150, 50, 50)
                
                #redraw buttons
                pygame.draw.rect(screen, main_color, main_button, border_radius=10)
                pygame.draw.rect(screen, quit_color, quit_button, border_radius=10)
                
                screen.blit(main_text_surface, main_text_surface.get_rect(center=main_button.center))
                screen.blit(quit_text_surface, quit_text_surface.get_rect(center=quit_button.center))
                
                pygame.display.flip()
                clock.tick(60)

    pygame.display.flip()
    clock.tick(FPS)