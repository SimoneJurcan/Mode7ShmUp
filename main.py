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
