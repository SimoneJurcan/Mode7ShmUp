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

    def draw(self, screen, camera_x, camera_y, horizon_screen_y, camera_angle):
     
        screen_x, screen_y, scale = project(
            self.x, self.y, self.z, camera_x, camera_y, horizon_screen_y, camera_angle
        )
        if scale <= 0:
            return
        r_outer = max(6, int(20 * scale))
        r_inner = max(3, int(10 * scale))
        c = COLOR_MAP.get(self.kind, (255, 255, 255))
        pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), r_outer + 2)
        pygame.draw.circle(screen, c, (screen_x, screen_y), r_outer)
        pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), r_inner)

    def apply(self, player, player_health, player_max_health):
        if self.kind == HEALTH:
            return min(player_health + self.amount, player_max_health)
        elif self.kind == SHIELD:
            player.add_shield(self.duration, cap=None)
            return player_health
        elif self.kind == FIRERATE:
            player.apply_fire_rate(mult=0.6, duration=self.duration, cap=None)
            return player_health
        return player_health
