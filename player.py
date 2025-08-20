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

class Player:
    def __init__(self, speed=1200, y_speed=650):
        self.x = 0.0
        self.y = 0.0
        self.speed = speed
        self.y_speed = y_speed

        self.bullets = []
        self.bullet_timer = 0.0
        self.current_weapon = REVOLVER

   
        self.heat = 0.0
        self.max_heat = 100.0
        self.overheated = False
        self.heat_cooldown_rate = 40.0
        self.heat_per_shot = 10.0
        self.overheat_threshold = self.max_heat      #
        self.recover_threshold  = 40.0             

        self.shield_timer = 0.0
        self.fire_rate_mult = 1.0
        self.fire_rate_timer = 0.0
   
    def handle_input(self, keys, dt):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y += self.y_speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y -= self.y_speed * dt

        
        self.x = max(X_MIN, min(X_MAX, self.x))
        self.y = max(Y_MIN, min(Y_MAX, self.y))

       
        if keys[pygame.K_1]:
            self.current_weapon = REVOLVER
        if keys[pygame.K_2]:
            self.current_weapon = SHOTGUN
        if keys[pygame.K_3]:
            self.current_weapon = MACHINE_GUN

    def update(self, dt, keys):
        self.handle_input(keys, dt)
        self.bullet_timer = max(0.0, self.bullet_timer - dt)

    
        if self.heat > 0.0:
            self.heat = max(0.0, self.heat - self.heat_cooldown_rate * dt)
     
        if self.overheated and self.heat <= self.recover_threshold:
            self.overheated = False

       
        if self.shield_timer > 0.0:
            self.shield_timer = max(0.0, self.shield_timer - dt)
        if self.fire_rate_timer > 0.0:
            self.fire_rate_timer = max(0.0, self.fire_rate_timer - dt)
            if self.fire_rate_timer == 0.0:
                self.fire_rate_mult = 1.0
