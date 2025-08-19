import pygame
import random
import math
from mode7 import project


ENEMY_SPEED = 180         
ENEMY_MAX_HEALTH = 3
ENEMY_MIN_Z = 800.0
ENEMY_MAX_Z = 1200.0


enemy_texture = None
enemy_fast_texture = None
enemy_tank_texture = None
boss1_texture = None
boss2_texture = None
_assets_initialized = False

def load_texture(path: str, use_colorkey: bool = False) -> pygame.Surface:
  
    img = pygame.image.load(path)
    if use_colorkey:
        surf = img.convert()
   
        surf.set_colorkey(surf.get_at((0, 0)))
        return surf
    else:
        return img.convert_alpha()

def init_enemy_assets():
 
    global _assets_initialized
    if _assets_initialized:
        return

    global enemy_texture, enemy_fast_texture, enemy_tank_texture, boss1_texture, boss2_texture

    
    enemy_texture       = load_texture('textures/enemy_alien.png',       use_colorkey=False)
    enemy_fast_texture  = load_texture('textures/enemy_alien_fast.png',  use_colorkey=False)
    enemy_tank_texture  = load_texture('textures/enemy_alien_tank.png',  use_colorkey=False)
    boss1_texture       = load_texture('textures/Boss1.png',             use_colorkey=False)
    boss2_texture       = load_texture('textures/Boss2.png',             use_colorkey=True)

    _assets_initialized = True
