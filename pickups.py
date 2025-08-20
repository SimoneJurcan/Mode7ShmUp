
import pygame
import random
from mode7 import project

HEALTH     = "HEALTH"
SHIELD     = "SHIELD"
FIRERATE   = "FIRERATE"


COLOR_MAP = {
    HEALTH:   (60, 220, 60),
    SHIELD:   (80, 180, 255),
    FIRERATE: (255, 180, 60),
}

class Pickup:
    def __init__(self, x, y, z, kind, amount=0, duration=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.kind = kind
        self.amount = amount  
        self.duration = duration  
        self.alive = True
     
        self.vx = random.uniform(-30, 30)
        self.vy = random.uniform(-30, 30)
        self.vz = -200.0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
