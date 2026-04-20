import pygame
import sys
import json
import os
import math
from physics import PhysicsWorld
import levels
from entities import Particle, Debris
import sound_gen

WIDTH, HEIGHT = 400, 600
FPS = 60

def draw_brutal_rect(surface, color, rect, border_radius=0):
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(*rect)
    shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.w, rect.h)
    pygame.draw.rect(surface, (31, 41, 55), shadow_rect, border_radius=border_radius)
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    pygame.draw.rect(surface, (31, 41, 55), rect, width=3, border_radius=border_radius)

def draw_brutal_circle(surface, color, center, radius):
    pygame.draw.circle(surface, (31, 41, 55), (center[0] + 4, center[1] + 4), radius)
    pygame.draw.circle(surface, color, center, radius)
    pygame.draw.circle(surface, (31, 41, 55), center, radius, width=3)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        sound_gen.generate_all()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Physics Box 2: Shield Edition")
        self.clock = pygame.time.Clock()
        self.state = "MENU"
        self.running = True
        
        base = os.path.dirname(os.path.dirname(__file__))
        self.snd_shoot = pygame.mixer.Sound(os.path.join(base, 'assets', 'shoot.wav'))
        self.snd_die = pygame.mixer.Sound(os.path.join(base, 'assets', 'explosion.wav'))
        self.snd_shield = pygame.mixer.Sound(os.path.join(base, 'assets', 'shield.wav'))
        self.snd_win = pygame.mixer.Sound(os.path.join(base, 'assets', 'win.wav'))
        self.snd_click = pygame.mixer.Sound(os.path.join(base, 'assets', 'click.wav'))
        self.snd_error = pygame.mixer.Sound(os.path.join(base, 'assets', 'error.wav'))
        
        self.settings = self.load_settings()
        self.physics = PhysicsWorld()
        self.physics.on_death = self.on_death
        self.physics.on_win = self.on_win
        self.physics.on_shield_pickup = self.on_shield_pickup
        
        self.current_level = 0
        self.max_levels = 3
        self.player = None
        self.goal = None
        self.is_dead = False
        self.dead_timer = 0

    def load_settings(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {"unlocked_level": 1, "volume": 1.0}

    def save_settings(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        with open(path, 'w') as f:
            json.dump(self.settings, f)

    def load_level(self, idx):
        if idx >= self.max_levels:
            idx = 0
        self.current_level = idx
        self.player, self.goal = levels.load_level(idx + 1, self.physics)
        self.is_dead = False
        self.state = "PLAYING"

    def restart_level(self):
        self.snd_click.play()
        self.load_level(self.current_level)

    def next_level(self):
        nl = self.current_level + 1
        if nl + 1 > self.settings.get("unlocked_level", 1):
            self.settings["unlocked_level"] = nl + 1
            self.save_settings()
        self.load_level(nl)

    def on_death(self):
        if self.is_dead: return
        if self.player and self.player.has_shield:
            self.player.has_shield = False
            self.player.body.velocity = (-self.player.body.velocity.x * 1.5, -600)
            self.snd_shield.play() # bounce sound!
            return
            
        self.is_dead = True
        self.snd_die.play()
        if self.player:
            px, py = self.player.body.position
            self.physics.remove_entity(self.player)
            self.player = None
            
            for _ in range(8):
                Debris(self.physics, px, py)
        self.dead_timer = pygame.time.get_ticks()

    def on_win(self):
        if self.state != "WIN":
            self.state = "WIN"
            self.snd_win.play()

    def on_shield_pickup(self, item_entity):
        if self.player:
            self.player.has_shield = True
        self.physics.remove_entity(item_entity)
        self.snd_shield.play()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)

    def handle_click(self, pos):
        if self.state == "MENU":
            play_btn = pygame.Rect(WIDTH//2 - 70, 300, 140, 70)
            if play_btn.collidepoint(pos):
                self.snd_click.play()
                self.state = "SELECT"
                
        elif self.state == "SELECT":
            home_btn = pygame.Rect(15, 15, 60, 45)
            if home_btn.collidepoint(pos):
                self.snd_click.play()
                self.state = "MENU"
                return
                
            reset_btn = pygame.Rect(WIDTH//2 - 80, HEIGHT - 80, 160, 40)
            if reset_btn.collidepoint(pos):
                self.snd_error.play() # Give a heavy thud feedback
                self.settings["unlocked_level"] = 1
                self.save_settings()
                return

            grid_start_y = 120
            for i in range(self.max_levels):
                col = i % 4
                row = i // 4
                bx = 40 + col * 75
                by = grid_start_y + row * 75
                rect = pygame.Rect(bx, by, 60, 60)
                if rect.collidepoint(pos):
                    if i < self.settings.get("unlocked_level", 1):
                        self.snd_click.play()
                        self.load_level(i)
                    else:
                        self.snd_error.play()
        
        elif self.state == "PLAYING":
            home_btn = pygame.Rect(15, 15, 45, 45)
            restart_btn = pygame.Rect(WIDTH - 60, 15, 45, 45)
            
            if home_btn.collidepoint(pos):
                self.snd_click.play()
                self.state = "SELECT"
                self.physics.clear()
            elif restart_btn.collidepoint(pos):
                self.restart_level()
            else:
                if self.player and not self.is_dead:
                    px, py = self.player.body.position
                    mx, my = pos
                    angle = math.atan2(my - py, mx - px)
                    self.player.apply_recoil(angle)
                    Particle(self.physics, px, py, angle)
                    self.snd_shoot.play()
                    
        elif self.state == "WIN":
            btn_rect = pygame.Rect(WIDTH//2 - 90, 400, 180, 50)
            if btn_rect.collidepoint(pos):
                self.snd_click.play()
                if self.current_level + 1 < self.max_levels:
                    self.next_level()
                else:
                    self.state = "MENU"

    def update(self):
        if self.state == "PLAYING" or self.state == "WIN":
            for e in self.physics.entities:
                if hasattr(e, 'update'):
                    e.update()
            self.physics.step(1.0 / FPS)
            
            if self.is_dead and pygame.time.get_ticks() - self.dead_timer > 1200:
                self.restart_level()

    def draw(self):
        self.screen.fill((240, 244, 248)) 
        
        for y in range(0, HEIGHT, 50):
            for x in range(0, WIDTH, 30):
                dx = x if y % 100 == 0 else x + 15
                points = [(dx, y), (dx+8, y), (dx+8, y+16), (dx+4, y+20), (dx, y+16)]
                pygame.draw.polygon(self.screen, (226, 232, 240), points)

        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "SELECT":
            self.draw_select()
        elif self.state == "PLAYING":
            self.physics.draw(self.screen)
            self.draw_hud()
        elif self.state == "WIN":
            self.physics.draw(self.screen)
            self.draw_win()
            
        pygame.display.flip()

    def draw_menu(self):
        font_large = pygame.font.SysFont("Verdana", 60, bold=True)
        txt = font_large.render("PHYSICS", True, (31, 41, 55))
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 120))
        
        txt2 = font_large.render("BOX 2", True, (139, 195, 74))
        txt2_shadow = font_large.render("BOX 2", True, (31, 41, 55))
        self.screen.blit(txt2_shadow, (WIDTH//2 - txt2.get_width()//2 + 4, 194))
        self.screen.blit(txt2, (WIDTH//2 - txt2.get_width()//2, 190))
        
        btn_rect = pygame.Rect(WIDTH//2 - 70, 300, 140, 70)
        draw_brutal_rect(self.screen, (0, 229, 255), btn_rect, 35)
        pygame.draw.polygon(self.screen, (31, 41, 55), [(WIDTH//2 - 10, 315), (WIDTH//2 - 10, 355), (WIDTH//2 + 20, 335)])

    def draw_select(self):
        home_btn = pygame.Rect(15, 15, 60, 45)
        draw_brutal_rect(self.screen, (251, 191, 36), home_btn, 10)
        font_sm = pygame.font.SysFont("Verdana", 14, bold=True)
        txt_h = font_sm.render("HOME", True, (31, 41, 55))
        self.screen.blit(txt_h, (15 + 30 - txt_h.get_width()//2, 15 + 23 - txt_h.get_height()//2))

        font = pygame.font.SysFont("Verdana", 32, bold=True)
        txt = font.render("LEVELS", True, (31, 41, 55))
        
        lbl_rect = pygame.Rect(WIDTH//2 - txt.get_width()//2 - 20, 15, txt.get_width() + 40, 50)
        draw_brutal_rect(self.screen, (255, 255, 255), lbl_rect, 10)
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 21))
        
        grid_start_y = 120
        font_lvl = pygame.font.SysFont("Verdana", 28, bold=True)
        for i in range(self.max_levels):
            col = i % 4
            row = i // 4
            bx = 40 + col * 75
            by = grid_start_y + row * 75
            rect = pygame.Rect(bx, by, 60, 60)
            
            is_unlocked = i < self.settings.get("unlocked_level", 1)
            color = (139, 195, 74) if is_unlocked else (156, 163, 175)
            draw_brutal_rect(self.screen, color, rect, 12)
            
            if is_unlocked:
                txt_lvl = font_lvl.render(str(i+1), True, (31, 41, 55))
            else:
                txt_lvl = font_lvl.render("x", True, (100, 110, 120))
            self.screen.blit(txt_lvl, (bx + 30 - txt_lvl.get_width()//2, by + 30 - txt_lvl.get_height()//2))

        # Reset Progress Button
        reset_btn = pygame.Rect(WIDTH//2 - 80, HEIGHT - 80, 160, 40)
        draw_brutal_rect(self.screen, (255, 82, 82), reset_btn, 10) # Red
        font_sm2 = pygame.font.SysFont("Verdana", 14, bold=True)
        txt_r = font_sm2.render("RESET PROGRESS", True, (31, 41, 55))
        self.screen.blit(txt_r, (WIDTH//2 - txt_r.get_width()//2, HEIGHT - 80 + 20 - txt_r.get_height()//2))

    def draw_hud(self):
        draw_brutal_circle(self.screen, (251, 191, 36), (37, 37), 22)
        pygame.draw.polygon(self.screen, (31, 41, 55), [(37, 24), (25, 34), (49, 34)])
        pygame.draw.rect(self.screen, (31, 41, 55), (28, 34, 18, 12))
        
        font_lvl = pygame.font.SysFont("Verdana", 24, bold=True)
        txt = font_lvl.render(f"LEVEL {self.current_level + 1}", True, (31, 41, 55))
        lbl_rect = pygame.Rect(WIDTH//2 - txt.get_width()//2 - 15, 15, txt.get_width() + 30, 42)
        draw_brutal_rect(self.screen, (255, 255, 255), lbl_rect, 15)
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 22))
        
        draw_brutal_circle(self.screen, (255, 82, 82), (WIDTH - 37, 37), 22)
        font_rst = pygame.font.SysFont("Verdana", 24, bold=True)
        txt_r = font_rst.render("R", True, (31, 41, 55))
        self.screen.blit(txt_r, (WIDTH - 37 - txt_r.get_width()//2, 37 - txt_r.get_height()//2))

    def draw_win(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont("Verdana", 50, bold=True)
        txt = font.render("CLEARED!", True, (255, 235, 59))
        
        txt_shadow = font.render("CLEARED!", True, (31, 41, 55))
        self.screen.blit(txt_shadow, (WIDTH//2 - txt.get_width()//2 + 5, 205))
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200))
        
        btn_rect = pygame.Rect(WIDTH//2 - 90, 400, 180, 50)
        draw_brutal_rect(self.screen, (0, 229, 255), btn_rect, 10)
        
        font_btn = pygame.font.SysFont("Verdana", 20, bold=True)
        if self.current_level + 1 < self.max_levels:
            txt_btn = font_btn.render("NEXT LEVEL", True, (31, 41, 55))
        else:
            txt_btn = font_btn.render("MAIN MENU", True, (31, 41, 55))
        self.screen.blit(txt_btn, (WIDTH//2 - txt_btn.get_width()//2, 413))

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
