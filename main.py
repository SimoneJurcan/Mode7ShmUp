import pygame
import math
import sys
import random
from settings import WIDTH, HEIGHT
from mode7 import render_mode7, project
from player import Player, REVOLVER, SHOTGUN, MACHINE_GUN
from enemy import (
    ENEMY_MAX_Z,
    Enemy, FastEnemy, TankEnemy, Boss1Enemy, Boss2Enemy,
    init_enemy_assets, draw_boss_health_bar
)
from pickups import Pickup, HEALTH, SHIELD, FIRERATE
from paths import rp

pygame.init()
pygame.mixer.init()
camera_angle = 0.0
START_BUTTON_X_OFFSET = -30
CONTROLS_X_OFFSET     = -30

revolver_sfx = pygame.mixer.Sound(rp("assets", "sfx", "revolver.ogg"))
shotgun_sfx  = pygame.mixer.Sound(rp("assets", "sfx", "shotgun.ogg"))
minigun_sfx  = pygame.mixer.Sound(rp("assets", "sfx", "minigun.ogg"))
revolver_sfx.set_volume(0.5)
shotgun_sfx.set_volume(0.6)
minigun_sfx.set_volume(0.5)

MUSIC_VOL_DEFAULT = 0.3
pygame.mixer.music.load(rp("assets", "music", "background_music.ogg"))
pygame.mixer.music.set_volume(MUSIC_VOL_DEFAULT)
pygame.mixer.music.play(-1)

enemy_hit_sfx = pygame.mixer.Sound(rp("assets", "sfx", "enemy_hit.ogg"))
player_hit_sfx = pygame.mixer.Sound(rp("assets", "sfx", "player_hit.ogg"))
enemy_hit_sfx.set_volume(0.3)
player_hit_sfx.set_volume(0.5)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

menu_bg   = pygame.image.load(rp("textures", "menu_bg.png")).convert()
defeat_bg = pygame.image.load(rp("textures", "defeat_bg.png")).convert()

CONTACT_Z = 280

sky_texture = pygame.image.load(rp("textures", "sky_night_fullres.png")).convert()
ground_texture = pygame.image.load(rp("textures", "planet.png")).convert()

_weapon_src = {
    REVOLVER: pygame.image.load(rp("textures", "revolver.png")).convert_alpha(),
    SHOTGUN: pygame.image.load(rp("textures", "shotgun.png")).convert_alpha(),
    MACHINE_GUN: pygame.image.load(rp("textures", "machinegun.png")).convert_alpha(),
}
weapon_icons_128 = {k: pygame.transform.scale(v, (128, 128)) for k, v in _weapon_src.items()}

FONT_32 = pygame.font.SysFont('Arial', 32)
FONT_64 = pygame.font.SysFont('Arial', 64, bold=True)

init_enemy_assets()

PLAYER_MAX_HEALTH = 50
HEALTH_REGEN_AMOUNT = 3
HEALTH_REGEN_INTERVAL = 3.0
REGEN_COOLDOWN = 5.0

ENEMY_BULLET_SPEED   = -900
ENEMY_BULLET_DAMAGE  = 4
ENEMY_FIRE_RATE_BASE = 0.5

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

def blit_cover(surface, image, scroll_amp=0, scroll_speed=0.0, nudge_x=0):
    w, h = surface.get_size()
    iw, ih = image.get_size()
    scale = max(w / iw, h / ih)
    sw, sh = int(iw * scale), int(ih * scale)
    img = pygame.transform.smoothscale(image, (sw, sh))
    oy = 0
    if scroll_amp:
        t = pygame.time.get_ticks() / 1000.0
        oy = int(scroll_amp * math.sin(t * scroll_speed))
    surface.blit(img, (w // 2 - sw // 2 + nudge_x, h // 2 - sh // 2 + oy))

def make_start_buttons(w, h):
    BTN_W = min(360, int(w * 0.5))
    BTN_H = 64
    GAP   = 16
    y0 = int(h * 0.48)
    cx = w // 2

    start = Button((0, y0, BTN_W, BTN_H), "START",  FONT_32, bg=(0,130,80))
    quitb = Button((0, y0 + BTN_H + GAP, BTN_W, BTN_H), "QUIT", FONT_32, bg=(146, 24, 60))

    start.rect.centerx = cx + START_BUTTON_X_OFFSET
    quitb.rect.centerx = cx + START_BUTTON_X_OFFSET
    return start, quitb

def draw_start_screen(screen, start_btn, quit_btn):
    w, h = screen.get_size()
    cx = w // 2
    blit_cover(screen, menu_bg, scroll_amp=10, scroll_speed=0.22)  

    
    start_btn.rect.centerx = cx + START_BUTTON_X_OFFSET
    quit_btn.rect.centerx  = cx + START_BUTTON_X_OFFSET
    start_btn.draw(screen)
    quit_btn.draw(screen)


    controls = FONT_32.render("Move: WASD   •   Shoot: SPACE   •   Pause: P", True, (220, 230, 240))
    rc = controls.get_rect(midbottom=(cx + CONTROLS_X_OFFSET, h - 28))
    screen.blit(controls, rc)

def make_end_buttons(w, h):
    BTN_W = min(360, int(w*0.5))
    BTN_H = 64
    GAP   = 16
    y0 = int(h*0.55)
    cx = w // 2
    restart = Button((0, y0, BTN_W, BTN_H), "RESTART",  FONT_32, bg=(0,110,160))
    menu    = Button((0, y0 + BTN_H + GAP, BTN_W, BTN_H), "MAIN MENU", FONT_32, bg=(90,90,90))
    quitb   = Button((0, y0 + 2*(BTN_H + GAP), BTN_W, BTN_H), "QUIT", FONT_32, bg=(146,24,60))
    restart.rect.centerx = menu.rect.centerx = quitb.rect.centerx = cx
    return restart, menu, quitb

def draw_end_screen(screen, wave, restart_btn, menu_btn, quit_btn, score=None):
    w, h = screen.get_size()
    cx = w // 2
    blit_cover(screen, defeat_bg, scroll_amp=6, scroll_speed=0.15)

    title = FONT_64.render("GAME OVER", True, (255, 90, 90))
    r_title = title.get_rect(midtop=(cx, int(h * 0.10)))
    screen.blit(title, r_title)

    y_info = r_title.bottom + 20
    wave_text = FONT_32.render(f"Reached Wave: {wave}", True, (255, 220, 220))
    screen.blit(wave_text, wave_text.get_rect(midtop=(cx, y_info)))

    if score is not None:
        score_text = FONT_32.render(f"Score: {score}", True, (255, 220, 220))
        screen.blit(score_text, score_text.get_rect(midtop=(cx, y_info + wave_text.get_height() + 8)))

    restart_btn.rect.centerx = menu_btn.rect.centerx = quit_btn.rect.centerx = cx
    restart_btn.draw(screen)
    menu_btn.draw(screen)
    quit_btn.draw(screen)

def draw_pause_screen(screen):
    w, h = screen.get_size()
    title = FONT_64.render("PAUSED", True, (255, 255, 0))
    screen.blit(title, (w // 2 - title.get_width() // 2, h // 2 - title.get_height() // 2))

def draw_parallax_sky(horizon_screen_y, camera_x, camera_angle):
    w, _ = screen.get_size()
    sky_offset_x = int((camera_angle % (2*math.pi)) / (2*math.pi) * w)
    sky_scaled = pygame.transform.smoothscale(sky_texture, (w, max(1, horizon_screen_y)))
    screen.blit(sky_scaled, (-sky_offset_x, 0))
    screen.blit(sky_scaled, (-sky_offset_x + w, 0))

def draw_bullet(bullet, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs):
    sx, sy, sc = project(bullet['x'], bullet['y'], bullet['z'],
                         camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs)
    r = max(2, int(6 * sc))
    pygame.draw.circle(screen, (100, 255, 100), (sx, sy), r)
    pygame.draw.circle(screen, (200, 255, 200), (sx, sy), r // 2)

def draw_enemy_sprite(screen, enemy, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs):
    x, y, z = enemy.get_pos()
    sx, sy, sc = project(x, y, z, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs)
    sc = max(0.1, min(1.0, sc))
    enemy_w = int(enemy.texture.get_width() * sc)
    enemy_h = int(enemy.texture.get_height() * sc)
    img = pygame.transform.scale(enemy.texture, (enemy_w, enemy_h))
    screen.blit(img, (sx - enemy_w // 2, sy - enemy_h // 2))
    return x, y, z

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

def draw_particle(p, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs):
    sx, sy, sc = project(p.x, p.y, p.z, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs)
    if sc > 0:
        radius = max(1, int(4 * sc * (p.lifetime / 0.6)))
        pygame.draw.circle(screen, p.color, (sx, sy), radius)

def spawn_enemy_shot(enemy, player):
    ex, ey, ez = enemy.get_pos()
    speed = ENEMY_BULLET_SPEED
    t = max(0.1, (ez - 0.0) / (-speed))
    vx = (player.x - ex) / t
    vy = (player.y - ey) / t
    vx += random.uniform(-80, 80) / t
    vy += random.uniform(-80, 80) / t
    return {'x': ex, 'y': ey, 'z': ez, 'vx': vx, 'vy': vy, 'vz': speed, 'damage': getattr(enemy, 'damage', ENEMY_BULLET_DAMAGE)}

def draw_enemy_bullet(eb, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs):
    sx, sy, sc = project(eb['x'], eb['y'], eb['z'],
                         camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs)
    r = max(2, int(5 * sc))
    pygame.draw.circle(screen, (255, 80, 80), (sx, sy), r)
    pygame.draw.circle(screen, (255, 220, 220), (sx, sy), r // 2)

GAME_STATE_MENU = 'MENU'
GAME_STATE_PLAYING = 'PLAYING'
GAME_STATE_PAUSED = 'PAUSED'
GAME_STATE_GAME_OVER = 'GAME_OVER'

class Particle:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.vx = random.uniform(-100, 100)
        self.vy = random.uniform(-100, 100)
        self.vz = random.uniform(50, 150)
        self.lifetime = random.uniform(0.3, 0.6)
        self.color = random.choice([(255,100,0), (255,200,0), (200,50,0)])

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.lifetime -= dt

def main():
    global screen, camera_angle
    game_state = GAME_STATE_MENU
    music_muted = False
    music_btn = None

    start_btn = quit_btn = None
    restart_btn = menu_btn = quit_btn_end = None

    def reset_game():
        nonlocal player, player_health, damage_timer, screen_flash_timer, wave, enemies, regen_timer, regen_tick_timer, particles, pickups, enemy_bullets
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
        enemy_bullets = []

    player = Player(speed=1000, y_speed=550)
    player_health = PLAYER_MAX_HEALTH
    damage_timer = 0.0
    screen_flash_timer = 0.0
    wave = 1
    enemies = []
    particles = []
    pickups = []
    enemy_bullets = []
    regen_timer = 0.0
    regen_tick_timer = 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        w, h = screen.get_size()

        if game_state == GAME_STATE_MENU:
            start_btn, quit_btn = make_start_buttons(w, h)
            restart_btn = menu_btn = quit_btn_end = None
            music_btn = None
        elif game_state == GAME_STATE_GAME_OVER:
            restart_btn, menu_btn, quit_btn_end = make_end_buttons(w, h)
            start_btn = quit_btn = None
            music_btn = None
        elif game_state == GAME_STATE_PAUSED:
            BTN_W, BTN_H = 240, 56
            label = "MUTE MUSIC" if not music_muted else "UNMUTE"
            music_btn = Button((w//2 - BTN_W//2, int(h*0.55), BTN_W, BTN_H), label, FONT_32, bg=(60,60,80))
            start_btn = quit_btn = restart_btn = menu_btn = quit_btn_end = None
        else:
            start_btn = quit_btn = restart_btn = menu_btn = quit_btn_end = None
            music_btn = None

       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE:
                new_width, new_height = event.size
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

            if game_state == GAME_STATE_MENU:
                if start_btn and start_btn.clicked(event):
                    reset_game(); game_state = GAME_STATE_PLAYING
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
        
                if music_btn and music_btn.clicked(event):
                    music_muted = not music_muted
                    pygame.mixer.music.set_volume(0.0 if music_muted else MUSIC_VOL_DEFAULT)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    game_state = GAME_STATE_PLAYING

            elif game_state == GAME_STATE_GAME_OVER:
                if restart_btn and restart_btn.clicked(event):
                    reset_game(); game_state = GAME_STATE_PLAYING
                elif menu_btn and menu_btn.clicked(event):
                    game_state = GAME_STATE_MENU
                    start_btn, quit_btn = make_start_buttons(w, h)
                elif quit_btn_end and quit_btn_end.clicked(event):
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        reset_game(); game_state = GAME_STATE_PLAYING
                    elif event.key == pygame.K_m:
                        game_state = GAME_STATE_MENU
                        start_btn, quit_btn = make_start_buttons(w, h)
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

 
        if game_state == GAME_STATE_MENU:
            draw_start_screen(screen, start_btn, quit_btn)
            pygame.display.flip()
            continue

        if game_state == GAME_STATE_PAUSED:
            draw_pause_screen(screen)
            if music_btn:
                music_btn.draw(screen)
            pygame.display.flip()
            continue

        if game_state == GAME_STATE_GAME_OVER:
            draw_end_screen(screen, wave, restart_btn, menu_btn, quit_btn_end, score=None)
            pygame.display.flip()
            continue

        
        screen_flash_timer = max(0.0, screen_flash_timer - dt)
        keys = pygame.key.get_pressed()
        ROT_SPEED = 1.6
        if keys[pygame.K_q]:
            camera_angle -= ROT_SPEED * dt
        if keys[pygame.K_e]:
            camera_angle += ROT_SPEED * dt

        player.update(dt, keys, camera_angle)
        player.shoot(keys)
        player.update_bullets(dt, ENEMY_MAX_Z + 200)

        camera_x, camera_y = player.get_camera()
        forward_ofs = camera_y
        bullets = player.get_bullets()

        current_width, current_height = screen.get_size()
        horizon_screen_y = current_height // 2 + 60 - int(player.get_pitch() * 0.2)

      
        regen_timer = max(0.0, regen_timer - dt)
        regen_tick_timer += dt
        if regen_timer <= 0 and regen_tick_timer >= HEALTH_REGEN_INTERVAL:
            if player_health < PLAYER_MAX_HEALTH:
                player_health += HEALTH_REGEN_AMOUNT
                player_health = min(player_health, PLAYER_MAX_HEALTH)
            regen_tick_timer = 0.0

        enemy_pos = [(e, e.get_pos()) for e in enemies if e.alive]

     
        for enemy, (ex, ey, ez) in enemy_pos:
            if not enemy.alive:
                continue
            rel_z = ez - forward_ofs
            if 120 < rel_z < ENEMY_MAX_Z + 200:
                rate = ENEMY_FIRE_RATE_BASE
                if isinstance(enemy, FastEnemy):
                    rate = 0.8
                elif isinstance(enemy, TankEnemy):
                    rate = 0.35
                elif isinstance(enemy, (Boss1Enemy, Boss2Enemy)):
                    rate = 1.2
                if random.random() < rate * dt:
                    enemy_bullets.append(spawn_enemy_shot(enemy, player))

        for enemy, (x, y, z) in enemy_pos:
            if not enemy.alive:
                continue
            _, _, scale = project(x, y, z, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs)
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

        player.cull_bullets(ENEMY_MAX_Z + 200)

      
        for enemy in enemies:
            if enemy.alive:
                try:
                    enemy.update(dt, player.x, player.y, forward_ofs)
                except TypeError:
                    enemy.update(dt)

       
        dead_enemy_bullets = []
        for eb in enemy_bullets:
            eb['x'] += eb['vx'] * dt
            eb['y'] += eb['vy'] * dt
            eb['z'] += eb['vz'] * dt

            rel_z = eb['z'] - forward_ofs
            if rel_z < 80:
                if abs(eb['x'] - player.x) < 90 and abs(eb['y'] - player.y) < 90:
                    if getattr(player, "shield_timer", 0.0) <= 0.0:
                        player_health -= eb['damage']
                        regen_timer = REGEN_COOLDOWN
                        player_hit_sfx.play()
                        screen_flash_timer = 0.2
                    dead_enemy_bullets.append(eb)
                    if player_health <= 0:
                        game_state = GAME_STATE_GAME_OVER
                        break

            if eb['z'] < -100:
                dead_enemy_bullets.append(eb)

        if dead_enemy_bullets:
            enemy_bullets = [b for b in enemy_bullets if b not in dead_enemy_bullets]

    
        for item in pickups:
            if not item.alive:
                continue

            item.update(dt)

            sx, sy, s = project(item.x, item.y, item.z, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs)
            px, py, _ = project(player.x, player.y, item.z, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs)

            dx = sx - px
            dy = sy - py
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < 200:
                pull = 480.0 * dt
                if dist > 1e-3:
                    item.vx += (px - sx) / dist * pull
                    item.vy += (py - sy) / dist * pull

            radius_screen = max(40, int(64 * s))
            hit_screen = (dx*dx + dy*dy) <= (radius_screen * radius_screen)

            wx = abs(item.x - player.x)
            wy = abs(item.y - player.y)
            wz_ok = (item.z - forward_ofs) < (CONTACT_Z + 120)
            hit_world = (wx < 130 and wy < 130 and wz_ok)

            if hit_screen or hit_world:
                player_health = item.apply(player, player_health, PLAYER_MAX_HEALTH)
                item.alive = False
                continue

            if item.z < 20:
                item.alive = False

        pickups = [p for p in pickups if p.alive]

      
        if all(not e.alive for e in enemies):
            wave += 1
            enemies.clear()
            if wave % 5 == 0:
                if wave % 10 == 0:
                    enemies.append(Boss2Enemy())
                else:
                    enemies.append(Boss1Enemy())
            else:
                for _ in range(wave + 2):
                    if wave < 3:
                        enemies.append(Enemy())
                    elif wave < 6:
                        enemies.append(random.choice([Enemy(), FastEnemy()]))
                    else:
                        enemies.append(random.choice([Enemy(), FastEnemy(), TankEnemy()]))

        for p in particles:
            p.update(dt)
        particles = [p for p in particles if p.lifetime > 0]

        enemies.sort(key=lambda e: e.z, reverse=True)

       
        screen.fill((0, 0, 0))
        cam_x = camera_x
        cam_y = camera_y

        draw_parallax_sky(horizon_screen_y, cam_x, camera_angle)
        render_mode7(screen, ground_texture, cam_x, cam_y, camera_angle, horizon_screen_y)
        draw_fog_gradient(horizon_screen_y)

        for enemy in enemies:
            if enemy.alive:
                draw_enemy_sprite(screen, enemy, cam_x, cam_y, horizon_screen_y, camera_angle, forward_ofs)

        boss = next((e for e in enemies if e.alive and isinstance(e, (Boss1Enemy, Boss2Enemy))), None)
        if boss:
            draw_boss_health_bar(screen, boss)

        for eb in enemy_bullets:
            draw_enemy_bullet(eb, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs)

        for pu in pickups:
            pu.draw(screen, cam_x, cam_y, horizon_screen_y, camera_angle)

        for bullet in bullets:
            draw_bullet(bullet, camera_x, camera_y, horizon_screen_y, camera_angle, forward_ofs)

        draw_hud(player, player_health, wave)
        draw_damage_flash(screen_flash_timer)

        for p in particles:
            draw_particle(p, cam_x, cam_y, horizon_screen_y, camera_angle, forward_ofs)

        pygame.display.flip()

if __name__ == '__main__':
    main()
