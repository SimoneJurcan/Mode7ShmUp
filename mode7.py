import pygame
import numpy as np
import math
from settings import WIDTH, HEIGHT, FOCAL_LEN, SCALE  

def project(x, y, z, camera_x, camera_y, horizon_screen_y):
    rel_x = x - camera_x
    rel_y = y - camera_y
    rel_z = max(0.1, z)  

    scale = FOCAL_LEN / rel_z

   
    surf = pygame.display.get_surface()
    w = surf.get_width() if surf else WIDTH

    screen_x = w // 2 + int(rel_x * scale)
    screen_y = horizon_screen_y - int(rel_y * scale) - int(scale * 20)  
    return screen_x, screen_y, scale

def render_mode7(surface, texture, camera_x, camera_y, camera_angle, horizon_screen_y):
    w, h = surface.get_size()
    mode7_height = h - horizon_screen_y
    if mode7_height <= 0:
        return

   
    lowres_w = max(160, w // 4)
    lowres_h = max(60,  mode7_height // 6)

    tex_w, tex_h = texture.get_width(), texture.get_height()
    tex_arr = pygame.surfarray.array3d(texture)  

    buffer = np.empty((lowres_h, lowres_w, 3), dtype=np.uint8)


    pitch = camera_y * 0.002

    cos_a = math.cos(camera_angle)
    sin_a = math.sin(camera_angle)
    cx = lowres_w // 2

    for sy in range(lowres_h):
       
        perspective = (FOCAL_LEN + pitch * sy) / (sy + 1)
        dy = perspective * SCALE

        for sx in range(lowres_w):
            dx = (sx - cx) * perspective

          
            world_x = camera_x + dx * cos_a - dy * sin_a
            world_y = camera_y + dx * sin_a + dy * cos_a

            tx = int(world_x) % tex_w
            ty = int(world_y) % tex_h

            buffer[sy, sx] = tex_arr[tx, ty]

   
    mode7_surface = pygame.surfarray.make_surface(buffer.swapaxes(0, 1))
    mode7_surface = pygame.transform.smoothscale(mode7_surface, (w, mode7_height))
    surface.blit(mode7_surface, (0, horizon_screen_y))
