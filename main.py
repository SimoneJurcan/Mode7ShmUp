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


class Button:
    def __init__(self, rect, text, font, bg=(36, 99, 72), fg=(255,255,255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg = bg
        self.fg = fg

    def draw(self, surface):
      
        shadow = self.rect.move(0, 4)
        pygame.draw.rect(surface, (0,0,0), shadow, border_radius=14)
        
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        mul = 1.15 if hovered else 1.0
        color = tuple(min(255, int(c*mul)) for c in self.bg)
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
     
        label = self.font.render(self.text, True, self.fg)
        surface.blit(label, (self.rect.centerx - label.get_width()//2,
                             self.rect.centery - label.get_height()//2))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))

def make_start_buttons(w, h):
    BTN_W = min(360, int(w*0.5))
    BTN_H = 64
    GAP   = 16
    y0 = int(h*0.48)
    start = Button((w//2 - BTN_W//2, y0, BTN_W, BTN_H), "START",  FONT_32, bg=(0,130,80))
    quitb = Button((w//2 - BTN_W//2, y0 + BTN_H + GAP, BTN_W, BTN_H), "QUIT", FONT_32, bg=(146, 24, 60))
    return start, quitb

def draw_start_screen(screen, start_btn, quit_btn):
    w, h = screen.get_size()
    screen.fill((14, 18, 24))
    PANEL_W = min(900, int(w*0.82))
    PANEL_H = min(560, int(h*0.76))
    panel   = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    panel.fill((22, 26, 34, 230))
    px = w//2 - PANEL_W//2
    py = h//2 - PANEL_H//2
    screen.blit(panel, (px, py))

    title = FONT_64.render("Starfall: Earth Defense", True, (0, 255, 190))
  
    controls = FONT_32.render("Move: WASD/Arrows   •   Shoot: SPACE   •   Pause: P", True, (200, 210, 220))
    screen.blit(title,    (w//2 - title.get_width()//2,    py + 40))
   
    start_btn.draw(screen)
    quit_btn.draw(screen)

    controls_y = py + PANEL_H - controls.get_height() - 32
    screen.blit(controls, (w//2 - controls.get_width()//2, controls_y))

def make_end_buttons(w, h):
    BTN_W = min(360, int(w*0.5))
    BTN_H = 64
    GAP   = 16
    y0 = int(h*0.55)
    restart = Button((w//2 - BTN_W//2, y0, BTN_W, BTN_H), "RESTART",  FONT_32, bg=(0,110,160))
    menu    = Button((w//2 - BTN_W//2, y0 + BTN_H + GAP, BTN_W, BTN_H), "MAIN MENU", FONT_32, bg=(90,90,90))
    quitb   = Button((w//2 - BTN_W//2, y0 + 2*(BTN_H + GAP), BTN_W, BTN_H), "QUIT", FONT_32, bg=(146,24,60))
    return restart, menu, quitb

def draw_end_screen(screen, wave, restart_btn, menu_btn, quit_btn, score=None):
    w, h = screen.get_size()
    screen.fill((16, 14, 18))
    PANEL_W = min(900, int(w*0.82))
    PANEL_H = min(560, int(h*0.76))
    panel   = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    panel.fill((30, 22, 28, 235))
    px = w//2 - PANEL_W//2
    py = h//2 - PANEL_H//2
    screen.blit(panel, (px, py))

    title = FONT_64.render("GAME OVER", True, (255, 90, 90))
    screen.blit(title, (w//2 - title.get_width()//2, py + 48))

    y_info = py + 48 + title.get_height() + 20
    wave_text = FONT_32.render(f"Reached Wave: {wave}", True, (255, 220, 220))
    screen.blit(wave_text, (w//2 - wave_text.get_width()//2, y_info))

    if score is not None:
        score_text = FONT_32.render(f"Score: {score}", True, (255, 220, 220))
        screen.blit(score_text, (w//2 - score_text.get_width()//2, y_info + wave_text.get_height() + 8))

    restart_btn.draw(screen)
    menu_btn.draw(screen)
    quit_btn.draw(screen)

def draw_pause_screen(screen):
    w, h = screen.get_size()
    title = FONT_64.render("PAUSED", True, (255, 255, 0))
    screen.blit(title, (w // 2 - title.get_width() // 2, h // 2 - title.get_height() // 2))


def draw_parallax_sky(horizon_screen_y, camera_x):
    w, _ = screen.get_size()
    sky_offset_x = -int(camera_x * 0.1) % w
    sky_scaled = pygame.transform.smoothscale(sky_texture, (w, max(1, horizon_screen_y)))
    screen.blit(sky_scaled, (sky_offset_x, 0))
    screen.blit(sky_scaled, (sky_offset_x - w, 0))  

def draw_bullet(bullet, camera_x, camera_y, horizon_screen_y):
    screen_x, screen_y, scale = project(bullet['x'], bullet['y'], bullet['z'], camera_x, camera_y, horizon_screen_y)
    r = max(2, int(6 * scale))
    pygame.draw.circle(screen, (100, 255, 100), (screen_x, screen_y), r)
    pygame.draw.circle(screen, (200, 255, 200), (screen_x, screen_y), r // 2)

def draw_hud(player, player_health, wave):
    w, h = screen.get_size()
    player_text = FONT_32.render(f'Player HP: {player_health}', True, (0,255,0) if player_health > 15 else (255,0,0))
    wave_text = FONT_32.render(f'Wave: {wave}', True, (255,255,0))
    screen.blit(player_text, (30, 30))
    screen.blit(wave_text, (30, 70))

    icon = weapon_icons_128[player.current_weapon]
    screen.blit(icon, (30, h - 158))

    
    if player.current_weapon == MACHINE_GUN:
        heat_percentage = player.heat / player.max_heat
        heat_color = (255, 100, 0) if not player.overheated else (255, 0, 0)
        heat_bar_width = 128
        heat_bar_height = 10
        pygame.draw.rect(screen, (50,50,50), (30, h - 178, heat_bar_width, heat_bar_height))
        pygame.draw.rect(screen, heat_color, (30, h - 178, int(heat_bar_width * heat_percentage), heat_bar_height))

    x0 = 30 + 128 + 16
    y0 = h - 158
    bar_w, bar_h = 160, 12

    shield_t = getattr(player, "shield_timer", 0.0)
    if shield_t > 0.0:
   
        shield_full = max(6.0, shield_t)
        ratio = min(1.0, shield_t / shield_full)
        pygame.draw.rect(screen, (30,30,30), (x0, y0, bar_w, bar_h))
        pygame.draw.rect(screen, (80, 180, 255), (x0, y0, int(bar_w * ratio), bar_h))

  
    fr_t = getattr(player, "fire_rate_timer", 0.0)
    if fr_t > 0.0:
        fr_full = max(6.0, fr_t)
        ratio = min(1.0, fr_t / fr_full)
        pygame.draw.rect(screen, (30,30,30), (x0, y0 + bar_h + 6, bar_w, bar_h))
        pygame.draw.rect(screen, (255, 180, 60), (x0, y0 + bar_h + 6, int(bar_w * ratio), bar_h))


def draw_damage_flash(timer):
    if timer > 0:
        w, h = screen.get_size()
        alpha = int(255 * (timer / 0.2))
        flash_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        flash_surface.fill((255, 0, 0, alpha))
        screen.blit(flash_surface, (0, 0))

def draw_fog_gradient(horizon_screen_y):
    w, _ = screen.get_size()
    fog_height = 120
    fog_surface = pygame.Surface((w, fog_height), pygame.SRCALPHA)
    fog_color = (230, 230, 240)
    for y in range(fog_height):
        distance_from_center = abs(y - fog_height // 2)
        alpha = int(255 * (1 - (distance_from_center / (fog_height // 2)))**1.5)
        color = (*fog_color, alpha)
        pygame.draw.line(fog_surface, color, (0, y), (w, y))
    screen.blit(fog_surface, (0, horizon_screen_y - fog_height // 2))

def draw_particle(p, camera_x, camera_y, horizon_screen_y):
    screen_x, screen_y, scale = project(p.x, p.y, p.z, camera_x, camera_y, horizon_screen_y)
    if scale > 0:
        radius = max(1, int(4 * scale * (p.lifetime / 0.6)))
        pygame.draw.circle(screen, p.color, (screen_x, screen_y), radius)


GAME_STATE_MENU = 'MENU'
GAME_STATE_PLAYING = 'PLAYING'
GAME_STATE_PAUSED = 'PAUSED'
GAME_STATE_GAME_OVER = 'GAME_OVER'

def main():
    global screen
    game_state = GAME_STATE_MENU

    def reset_game():
        nonlocal player, player_health, damage_timer, screen_flash_timer, wave, enemies, regen_timer, regen_tick_timer, particles, pickups
        player = Player(speed=1000, y_speed=550) 
        player_health = PLAYER_MAX_HEALTH
        damage_timer = 0.0
        screen_flash_timer = 0.0
        wave = 1
        enemies = [Enemy() for _ in range(wave + 2)]
        regen_timer = 0.0
        regen_tick_timer = 0.0
        particles = []
        pickups = [] 

  
    player = Player(speed=1000, y_speed=550)
    player_health = PLAYER_MAX_HEALTH
    damage_timer = 0.0
    screen_flash_timer = 0.0
    wave = 1
    enemies = []
    particles = []
    pickups = []  
    regen_timer = 0.0
    regen_tick_timer = 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        w, h = screen.get_size()

        start_btn = quit_btn = None
        restart_btn = menu_btn = quit_btn_end = None
        if game_state == GAME_STATE_MENU:
            start_btn, quit_btn = make_start_buttons(w, h)
        elif game_state == GAME_STATE_GAME_OVER:
            restart_btn, menu_btn, quit_btn_end = make_end_buttons(w, h)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE:
                new_width, new_height = event.size
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

   
            if game_state == GAME_STATE_MENU:
                if start_btn and start_btn.clicked(event):
                    reset_game()
                    game_state = GAME_STATE_PLAYING
                elif quit_btn and quit_btn.clicked(event):
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        reset_game(); game_state = GAME_STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

       
            elif game_state == GAME_STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    game_state = GAME_STATE_PAUSED

          
            elif game_state == GAME_STATE_PAUSED:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    game_state = GAME_STATE_PLAYING

            elif game_state == GAME_STATE_GAME_OVER:
                if restart_btn and restart_btn.clicked(event):
                    reset_game(); game_state = GAME_STATE_PLAYING
                elif menu_btn and menu_btn.clicked(event):
                    game_state = GAME_STATE_MENU
                elif quit_btn_end and quit_btn_end.clicked(event):
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        reset_game(); game_state = GAME_STATE_PLAYING
                    elif event.key == pygame.K_m:
                        game_state = GAME_STATE_MENU
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

        
        if game_state == GAME_STATE_MENU:
            draw_start_screen(screen, start_btn, quit_btn)
            pygame.display.flip()
            continue

        if game_state == GAME_STATE_PAUSED:
            draw_pause_screen(screen)
            pygame.display.flip()
            continue

        if game_state == GAME_STATE_GAME_OVER:
            draw_end_screen(screen, wave, restart_btn, menu_btn, quit_btn_end, score=None)
            pygame.display.flip()
            continue

 
        screen_flash_timer = max(0.0, screen_flash_timer - dt)
        keys = pygame.key.get_pressed()
        player.update(dt, keys)
        player.shoot(keys)
        player.update_bullets(dt, ENEMY_MAX_Z + 200)
        camera_x, camera_y = player.get_camera()
        bullets = player.get_bullets()

        current_width, current_height = screen.get_size()
        horizon_screen_y = current_height // 2 + 60 - int(camera_y * 0.2)

      
        regen_timer = max(0.0, regen_timer - dt)
        regen_tick_timer += dt
        if regen_timer <= 0 and regen_tick_timer >= HEALTH_REGEN_INTERVAL:
            if player_health < PLAYER_MAX_HEALTH:
                player_health += HEALTH_REGEN_AMOUNT
                player_health = min(player_health, PLAYER_MAX_HEALTH)
            regen_tick_timer = 0.0

   
        enemy_pos = [(e, e.get_pos()) for e in enemies if e.alive]

      
        collided = []
        for enemy, (_, _, z) in enemy_pos:
            if z < CONTACT_Z:
                enemy.alive = False
                collided.append(enemy)

        if collided:
            total_damage = sum(e.damage for e in collided)
         
            if getattr(player, "shield_timer", 0.0) > 0.0:
                total_damage = 0
            player_health -= total_damage
            regen_timer = REGEN_COOLDOWN
            player_hit_sfx.play()  
            screen_flash_timer = 0.2
            if player_health <= 0:
                game_state = GAME_STATE_GAME_OVER

       
        for enemy, (x, y, z) in enemy_pos:
            if not enemy.alive:
                continue
            _, _, scale = project(x, y, z, camera_x, camera_y, horizon_screen_y)
            scale = max(0.1, min(1.0, scale))
            hitbox_x, hitbox_y, hitbox_z = enemy.get_hitbox_size(scale)

            for bullet in bullets:
                dx = bullet['x'] - x
                dy = bullet['y'] - y
                dz = bullet['z'] - z
                if abs(dx) < hitbox_x and abs(dy) < hitbox_y and abs(dz) < hitbox_z:
                    enemy.health -= bullet['damage']
                    player.kill_bullet(bullet)
                    if enemy.health <= 0:
                        enemy_hit_sfx.play()
                        enemy.alive = False
                        for _ in range(20):
                            particles.append(Particle(x, y, z))

                   
                        drop_roll = random.random()
                        if drop_roll < 0.10:  
                            pickups.append(Pickup(x, y, z, HEALTH, amount=8))
                        elif drop_roll < 0.16:  
                            pickups.append(Pickup(x, y, z, SHIELD, duration=6.0))
                        elif drop_roll < 0.22:  
                            pickups.append(Pickup(x, y, z, FIRERATE, duration=6.0))
