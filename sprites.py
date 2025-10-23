import os
import sys
import pygame


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # pyinstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_frames(sheet, num_frames, width, height):
    frames = []
    for i in range(num_frames):
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (i * width, 0, width, height))
        frames.append(frame)
    return frames


def load_sprites():
    idle = pygame.image.load(resource_path("Pink_Monster_Idle_4.png")).convert_alpha()
    run = pygame.image.load(resource_path("Pink_Monster_Run_6.png")).convert_alpha()
    jump = pygame.image.load(resource_path("Pink_Monster_Jump_8.png")).convert_alpha()
    dust = pygame.image.load(resource_path("Double_Jump_Dust_5.png")).convert_alpha()
    hurt = pygame.image.load(resource_path("Pink_Monster_Hurt_4.png")).convert_alpha()
    attack = pygame.image.load(resource_path("Pink_Monster_Attack1_4.png")).convert_alpha()
    walk_dust = pygame.image.load(resource_path("Walk_Run_Push_Dust_6.png")).convert_alpha()
    death = pygame.image.load(resource_path("Pink_Monster_Death_8.png")).convert_alpha()
    parry = pygame.image.load(resource_path("Pink_Monster_Push_6.png")).convert_alpha()

    idle_frames = get_frames(idle, 4, 32, 32)
    run_frames = get_frames(run, 6, 32, 32)
    jump_frames = get_frames(jump, 8, 32, 32)
    dust_frames = get_frames(dust, 5, 32, 32)
    hurt_frames = get_frames(hurt, 4, 32, 32)
    attack_frames = get_frames(attack, 6, 32, 32)
    walk_dust_frames = get_frames(walk_dust, 6, 32, 32)
    death_frames = get_frames(death, 8, 32, 32)
    parry_frames = get_frames(parry, 6, 32, 32)

    return idle_frames, run_frames, jump_frames, dust_frames, attack_frames, walk_dust_frames, hurt_frames, death_frames, parry_frames


def load_boss_sprites():
    boss_idle = pygame.image.load(resource_path("Golem_Idle_4.png")).convert_alpha()
    boss_glow = pygame.image.load(resource_path("Golem_Glow_8.png")).convert_alpha()
    boss_attack = pygame.image.load(resource_path("Golem_Attack_5.png")).convert_alpha()
    boss_death = pygame.image.load(resource_path("Golem_Death_14.png")).convert_alpha()
    boss_defense = pygame.image.load(resource_path("Golem_Defense_8.png")).convert_alpha()

    boss_idle_frames = get_frames(boss_idle, 4, 100, 100)
    boss_glow_frames = get_frames(boss_glow, 8, 100, 100)
    boss_attack_frames = get_frames(boss_attack, 5, 100, 100)
    boss_death_frames = get_frames(boss_death, 14, 100, 100)
    boss_defense_frames = get_frames(boss_defense, 8, 100, 100)

    return boss_idle_frames, boss_glow_frames, boss_attack_frames, boss_death_frames, boss_defense_frames
