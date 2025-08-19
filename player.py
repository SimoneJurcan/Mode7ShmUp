import pygame
import random
import os
pygame.mixer.init()

revolver_sfx = pygame.mixer.Sound("assets/sfx/revolver.ogg")
shotgun_sfx  = pygame.mixer.Sound("assets/sfx/shotgun.ogg")
minigun_sfx  = pygame.mixer.Sound("assets/sfx/minigun.ogg")

revolver_sfx.set_volume(0.6)
shotgun_sfx.set_volume(0.7)
minigun_sfx.set_volume(0.5)



REVOLVER = 'REVOLVER'
SHOTGUN = 'SHOTGUN'
MACHINE_GUN = 'MACHINE_GUN'

WEAPONS = {
    REVOLVER:    {'cooldown': 0.5, 'bullets': 1, 'spread': 0.0, 'damage': 3.0,  'bullet_speed': 1200},
    SHOTGUN:     {'cooldown': 0.8, 'bullets': 4, 'spread': 0.4, 'damage': 1.5,  'bullet_speed': 1000},
    MACHINE_GUN: {'cooldown': 0.1, 'bullets': 1, 'spread': 0.1, 'damage': 0.6,  'bullet_speed': 1400}
}


BASE_SPREAD_VEL = 400.0   
X_MIN, X_MAX = -800.0, 800.0  
Y_MIN, Y_MAX = -200.0, 200.0 
