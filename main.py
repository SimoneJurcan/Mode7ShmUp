import pygame
import sys
import random
from settings import WIDTH, HEIGHT
from mode7 import render_mode7, project
from player import Player, REVOLVER, SHOTGUN, MACHINE_GUN
from enemy import (
    ENEMY_MAX_Z,
    Enemy, FastEnemy, TankEnemy, Boss1Enemy, Boss2Enemy,
    init_enemy_assets, draw_enemy, draw_boss_health_bar
)
from pickups import Pickup, HEALTH, SHIELD, FIRERATE  



pygame.init()
pygame.mixer.init()


revolver_sfx = pygame.mixer.Sound("assets/sfx/revolver.ogg")
shotgun_sfx  = pygame.mixer.Sound("assets/sfx/shotgun.ogg")
minigun_sfx  = pygame.mixer.Sound("assets/sfx/minigun.ogg")

revolver_sfx.set_volume(0.5)
shotgun_sfx.set_volume(0.6)
minigun_sfx.set_volume(0.5)


pygame.mixer.music.load("assets/music/background_music.ogg")
pygame.mixer.music.set_volume(0.3)  
pygame.mixer.music.play(-1)         


enemy_hit_sfx = pygame.mixer.Sound("assets/sfx/enemy_hit.ogg")
player_hit_sfx = pygame.mixer.Sound("assets/sfx/player_hit.ogg")
enemy_hit_sfx.set_volume(0.3)
player_hit_sfx.set_volume(0.5)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

CONTACT_Z = 280  


sky_texture = pygame.image.load('textures/sky_night_fullres.png').convert()
ground_texture = pygame.image.load('textures/planet.png').convert()


_weapon_src = {
    REVOLVER: pygame.image.load('textures/revolver.png').convert_alpha(),
    SHOTGUN: pygame.image.load('textures/shotgun.png').convert_alpha(),
    MACHINE_GUN: pygame.image.load('textures/machinegun.png').convert_alpha(),
}
weapon_icons_128 = {
    k: pygame.transform.scale(v, (128, 128)) for k, v in _weapon_src.items()
}


FONT_32 = pygame.font.SysFont('Arial', 32)
FONT_64 = pygame.font.SysFont('Arial', 64, bold=True)

init_enemy_assets()

PLAYER_MAX_HEALTH = 50
HEALTH_REGEN_AMOUNT = 3
HEALTH_REGEN_INTERVAL = 3.0
REGEN_COOLDOWN = 5.0
