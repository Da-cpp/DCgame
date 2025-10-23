import os
import sys
import pygame

def resource_path(relative_path):
    #Get absolute path to resource for dev and PyInstaller.
    try:
        # PyInstaller stores files in a temporary folder called _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_sound(filename, volume=1.0):
    #Load and return a pygame sound safely
    path = resource_path(filename)
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except pygame.error as e:
        print(f"[WARN] Could not load sound: {path} — {e}")
        return None
    
def play_music(filename, volume=1.0, loops=-1):
    #safely play bg music
    path = resource_path(filename)
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)
    except pygame.error as e:
        print(f"[WARN] Could not play music: {path} — {e}")

