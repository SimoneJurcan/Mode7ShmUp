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


class Enemy:
    def __init__(self):
       
        self.base_x = random.uniform(-600, 600)
        self.base_y = random.uniform(-150, 150)
        self.z = random.uniform(ENEMY_MIN_Z, ENEMY_MAX_Z + 600)

  
        self.wave_amp_x = random.randint(100, 350)
        self.wave_freq_x = random.uniform(0.8, 3.0)   
        self.wave_phase_x = random.uniform(0, math.pi * 2)

        self.wave_amp_y = random.randint(50, 150)
        self.wave_freq_y = random.uniform(0.8, 3.0)  
        self.wave_phase_y = random.uniform(0, math.pi * 2)

        self.health = ENEMY_MAX_HEALTH
        self.alive = True
        self.t = random.uniform(0, 1000)
        self.texture = enemy_texture
        self.speed = ENEMY_SPEED
        self.damage = 3

    def get_hitbox_size(self, scale):
        width = int(self.texture.get_width() * scale)
        height = int(self.texture.get_height() * scale)
        hitbox_x = width // 2
        hitbox_y = height // 2
        hitbox_z = 100  
        return hitbox_x, hitbox_y, hitbox_z

    def update(self, dt):
        self.z -= self.speed * dt
        self.t += dt
        if self.z < 250:
    
            self.base_x = random.uniform(-600, 600)
            self.base_y = random.uniform(-150, 150)
            self.z = random.uniform(ENEMY_MIN_Z, ENEMY_MAX_Z + 600)

    def get_pos(self):
        x_offset = self.wave_amp_x * math.sin(self.wave_freq_x * self.t + self.wave_phase_x)
        y_offset = self.wave_amp_y * math.sin(self.wave_freq_y * self.t + self.wave_phase_y)
        x = self.base_x + x_offset
        y = self.base_y + y_offset
        z = self.z
        return x, y, z

class FastEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.health = 1
        self.speed = ENEMY_SPEED * 1.3
        self.texture = enemy_fast_texture
        self.damage = 1

class TankEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.health = ENEMY_MAX_HEALTH * 2
        self.speed = ENEMY_SPEED * 0.5
        self.texture = enemy_tank_texture
        self.damage = 5

class Boss1Enemy(Enemy):
    def __init__(self):
        super().__init__()
        self.health = ENEMY_MAX_HEALTH * 30
        self.speed = ENEMY_SPEED * 0.4
        self.texture = boss1_texture
        self.damage = 15
        self.base_x = 0
        self.wave_amp = 200 

    
        self.wave_freq_x = 1.2
        self.wave_freq_y = 0.8

    def get_hitbox_size(self, scale):
         base_xy = 180 
         base_z  = 220  
         s = max(0.1, min(1.0, scale))
         return (int(base_xy * s), int(base_xy * s), int(base_z * s))

    def get_pos(self):
      
        x = self.base_x + self.wave_amp * math.sin(self.wave_freq_x * self.t + self.wave_phase_x)
        y = self.base_y + (self.wave_amp * 0.5) * math.sin(self.wave_freq_y * self.t + self.wave_phase_y)
        return x, y, self.z

class Boss2Enemy(Enemy):
    def __init__(self):
        super().__init__()
        self.health = ENEMY_MAX_HEALTH * 35
        self.speed = ENEMY_SPEED * 0.3
        self.texture = boss2_texture
        self.damage = 20
        self.base_x = 0
        self.wave_amp = 150  

        self.wave_freq_x = 1.0
        self.wave_freq_y = 0.7

    def get_hitbox_size(self, scale):
        base_xy = 180 
        base_z  = 220  
        s = max(0.1, min(1.0, scale))
        return (int(base_xy * s), int(base_xy * s), int(base_z * s))

    def get_pos(self):
        x = self.base_x + self.wave_amp * math.sin(self.wave_freq_x * self.t + self.wave_phase_x)
        y = self.base_y + (self.wave_amp * 0.5) * math.sin(self.wave_freq_y * self.t + self.wave_phase_y)
        return x, y, self.z


def draw_enemy(screen, enemy, camera_x, camera_y, horizon_screen_y):
    x, y, z = enemy.get_pos()
    screen_x, screen_y, scale = project(x, y, z, camera_x, camera_y, horizon_screen_y)
    scale = max(0.1, min(1.0, scale))
    enemy_w = int(enemy.texture.get_width() * scale)
    enemy_h = int(enemy.texture.get_height() * scale)
    enemy_img = pygame.transform.scale(enemy.texture, (enemy_w, enemy_h))
    screen.blit(enemy_img, (screen_x - enemy_w // 2, screen_y - enemy_h // 2))
    return x, y, z

def draw_boss_health_bar(screen, enemy):
    if isinstance(enemy, (Boss1Enemy, Boss2Enemy)):
        current_width, _ = screen.get_size()
        max_health = ENEMY_MAX_HEALTH * (30 if isinstance(enemy, Boss1Enemy) else 35)
        health_percentage = max(0.0, min(1.0, enemy.health / max_health))

        bar_width = int(current_width * 0.8)
        bar_height = 20
        bar_x = (current_width - bar_width) // 2
        bar_y = 110

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * health_percentage), bar_height))
