import pygame
import random
import math
from paths import rp
pygame.mixer.init()

revolver_sfx = pygame.mixer.Sound(rp('assets','sfx','revolver.ogg'))
shotgun_sfx  = pygame.mixer.Sound(rp('assets','sfx','shotgun.ogg'))
minigun_sfx  = pygame.mixer.Sound(rp('assets','sfx','minigun.ogg'))

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



PITCH_MIN, PITCH_MAX = -300.0, 300.0 

class Player:
    def __init__(self, speed=1200, y_speed=650):
 
        self.x = 0.0
        self.y = 0.0

    
        self.speed = speed      
        self.y_speed = y_speed 


        self.pitch = 0.0
        self.pitch_speed = y_speed  

        
        self.angle = 0.0
        self.turn_speed = 1.6

    
        self.bullets = []
        self.bullet_timer = 0.0
        self.current_weapon = REVOLVER

      
        self.heat = 0.0
        self.max_heat = 100.0
        self.overheated = False
        self.heat_cooldown_rate = 40.0
        self.heat_per_shot = 10.0
        self.overheat_threshold = self.max_heat
        self.recover_threshold  = 40.0

    
        self.shield_timer = 0.0
        self.fire_rate_mult = 1.0
        self.fire_rate_timer = 0.0

    def handle_input(self, keys, dt, camera_angle):
     
        if camera_angle is None:
            ca, sa = 1.0, 0.0
        else:
            ca = math.cos(camera_angle)
            sa = math.sin(camera_angle)

        fwd_x,  fwd_y   = -sa,  ca
        right_x, right_y =  ca,  sa

        move_x = 0.0
        move_y = 0.0

        if keys[pygame.K_w]:
            move_x += fwd_x
            move_y += fwd_y
        if keys[pygame.K_s]:
            move_x -= fwd_x
            move_y -= fwd_y
        if keys[pygame.K_d]:
            move_x += right_x
            move_y += right_y
        if keys[pygame.K_a]:
            move_x -= right_x
            move_y -= right_y

  
        mag = math.hypot(move_x, move_y)
        if mag > 1e-6:
            move_x /= mag
            move_y /= mag
            self.x += move_x * self.speed * dt
            self.y += move_y * self.speed * dt

    
        if keys[pygame.K_UP]:
            self.pitch += self.pitch_speed * dt
        if keys[pygame.K_DOWN]:
            self.pitch -= self.pitch_speed * dt
        self.pitch = max(PITCH_MIN, min(PITCH_MAX, self.pitch))

        
        if keys[pygame.K_1]:
            self.current_weapon = REVOLVER
        if keys[pygame.K_2]:
            self.current_weapon = SHOTGUN
        if keys[pygame.K_3]:
            self.current_weapon = MACHINE_GUN

    
       

    def update(self, dt, keys, camera_angle=None):
        self.handle_input(keys, dt, camera_angle)

       
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

    def shoot(self, keys):
        weapon = WEAPONS[self.current_weapon]
        can_shoot = not (self.current_weapon == MACHINE_GUN and self.overheated)

        if keys[pygame.K_SPACE] and self.bullet_timer <= 0.0 and can_shoot:
            for _ in range(weapon['bullets']):
                self.bullets.append({
                    'x': self.x,
                    'y': self.y,
                    'z': 0.0,
                    'spread_x': random.uniform(-BASE_SPREAD_VEL, BASE_SPREAD_VEL) * weapon['spread'],
                    'damage': weapon['damage'],
                    'speed': weapon['bullet_speed']
                })
            self.bullet_timer = weapon['cooldown'] * self.fire_rate_mult

     
            if self.current_weapon == REVOLVER:
                revolver_sfx.play()
            elif self.current_weapon == SHOTGUN:
                shotgun_sfx.play()
            elif self.current_weapon == MACHINE_GUN:
                minigun_sfx.play()

  
            if self.current_weapon == MACHINE_GUN:
                self.heat = min(self.overheat_threshold, self.heat + self.heat_per_shot)
                if self.heat >= self.overheat_threshold:
                    self.overheated = True

    def update_bullets(self, dt, max_z):
        for b in self.bullets:
            b['z'] += b['speed'] * dt
            b['x'] += b['spread_x'] * dt
        self.cull_bullets(max_z)

    def kill_bullet(self, bullet_dict):
        bullet_dict['dead'] = True

    def cull_bullets(self, max_z):
        self.bullets = [b for b in self.bullets if not b.get('dead') and b['z'] < max_z]

    def get_camera(self):
        
        return self.x, self.y

    def get_forward(self) -> float:
  
        return self.y

    def get_pitch(self):

        return self.pitch

    def get_bullets(self):
        return tuple(self.bullets)

    def apply_fire_rate(self, mult, duration, cap=None):
        self.fire_rate_mult = min(self.fire_rate_mult, mult)
        self.fire_rate_timer += duration
        if cap is not None:
            self.fire_rate_timer = min(self.fire_rate_timer, cap)

    def add_shield(self, duration, cap=None):
        self.shield_timer += duration
        if cap is not None:
            self.shield_timer = min(self.shield_timer, cap)
