import pygame
from renderer import draw_brutal_rect, draw_brutal_circle, draw_entities
from ui import Button
from constants import WIDTH, HEIGHT
import math
from entities import Particle

class GameState:
    def __init__(self, game):
        self.game = game

    def handle_click(self, pos): pass
    def update(self): pass
    def draw(self): pass


class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.play_btn = Button(game, WIDTH//2 - 70, 300, 140, 70, (0, 229, 255), radius=35)

    def handle_click(self, pos):
        if self.play_btn.is_clicked(pos):
            self.game.change_state("SELECT")

    def draw(self):
        txt = self.game.get_text("PHYSICS", 60, (31, 41, 55))
        self.game.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 120))
        
        txt2 = self.game.get_text("BOX 2", 60, (139, 195, 74))
        txt2_shadow = self.game.get_text("BOX 2", 60, (31, 41, 55))
        self.game.screen.blit(txt2_shadow, (WIDTH//2 - txt2.get_width()//2 + 4, 194))
        self.game.screen.blit(txt2, (WIDTH//2 - txt2.get_width()//2, 190))
        
        self.play_btn.draw(self.game.screen)
        pygame.draw.polygon(self.game.screen, (31, 41, 55), [(WIDTH//2 - 10, 315), (WIDTH//2 - 10, 355), (WIDTH//2 + 20, 335)])


class SelectState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.home_btn = Button(game, 15, 15, 60, 45, (251, 191, 36), "HOME", 14, 10)
        self.reset_btn = Button(game, WIDTH//2 - 80, HEIGHT - 80, 160, 40, (255, 82, 82), "RESET PROGRESS", 14, 10, click_sound=game.snd_error)
        
        self.level_btns = []
        grid_start_y = 120
        for i in range(self.game.max_levels):
            col = i % 4
            row = i // 4
            bx = 40 + col * 75
            by = grid_start_y + row * 75
            
            is_unlocked = i < self.game.settings.get("unlocked_level", 1)
            color = (139, 195, 74) if is_unlocked else (156, 163, 175)
            text = str(i+1) if is_unlocked else "x"
            tcolor = (31, 41, 55) if is_unlocked else (100, 110, 120)
            self.level_btns.append(Button(game, bx, by, 60, 60, color, text, 28, 12, tcolor))

    def handle_click(self, pos):
        if self.home_btn.is_clicked(pos):
            self.game.change_state("MENU")
            return
            
        if self.reset_btn.is_clicked(pos):
            self.game.settings["unlocked_level"] = 1
            self.game.save_settings()
            self.game.change_state("SELECT")
            return

        for i, btn in enumerate(self.level_btns):
            if btn.is_clicked(pos):
                if i < self.game.settings.get("unlocked_level", 1):
                    self.game.load_level(i)
                else:
                    self.game.snd_error.play()

    def draw(self):
        self.home_btn.draw(self.game.screen)

        txt = self.game.get_text("LEVELS", 32, (31, 41, 55))
        lbl_rect = pygame.Rect(WIDTH//2 - txt.get_width()//2 - 20, 15, txt.get_width() + 40, 50)
        draw_brutal_rect(self.game.screen, (255, 255, 255), lbl_rect, 10)
        self.game.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 21))
        
        for btn in self.level_btns:
            btn.draw(self.game.screen)

        self.reset_btn.draw(self.game.screen)


class PlayState(GameState):
    def handle_click(self, pos):
        home_btn = pygame.Rect(15, 15, 45, 45)
        restart_btn = pygame.Rect(WIDTH - 60, 15, 45, 45)
        
        if home_btn.collidepoint(pos):
            self.game.snd_click.play()
            self.game.change_state("SELECT")
            self.game.physics.clear()
        elif restart_btn.collidepoint(pos):
            self.game.restart_level()
        else:
            if self.game.player and not self.game.is_dead:
                px, py = self.game.player.body.position
                mx, my = pos
                angle = math.atan2(my - py, mx - px)
                self.game.player.apply_recoil(angle)
                Particle(self.game.physics, px, py, angle)
                self.game.snd_shoot.play()

    def update(self):
        for e in self.game.physics.entities:
            if hasattr(e, 'update'):
                e.update()
        from constants import FPS
        self.game.physics.step(1.0 / FPS)
        
        if self.game.is_dead and pygame.time.get_ticks() - self.game.dead_timer > 1200:
            self.game.restart_level()

    def draw(self):
        draw_entities(self.game.screen, self.game.physics)
        
        draw_brutal_circle(self.game.screen, (251, 191, 36), (37, 37), 22)
        pygame.draw.polygon(self.game.screen, (31, 41, 55), [(37, 24), (25, 34), (49, 34)])
        pygame.draw.rect(self.game.screen, (31, 41, 55), (28, 34, 18, 12))
        
        txt = self.game.get_text(f"LEVEL {self.game.current_level + 1}", 24, (31, 41, 55))
        lbl_rect = pygame.Rect(WIDTH//2 - txt.get_width()//2 - 15, 15, txt.get_width() + 30, 42)
        draw_brutal_rect(self.game.screen, (255, 255, 255), lbl_rect, 15)
        self.game.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 22))
        
        draw_brutal_circle(self.game.screen, (255, 82, 82), (WIDTH - 37, 37), 22)
        txt_r = self.game.get_text("R", 24, (31, 41, 55))
        self.game.screen.blit(txt_r, (WIDTH - 37 - txt_r.get_width()//2, 37 - txt_r.get_height()//2))


class WinState(GameState):
    def __init__(self, game):
        super().__init__(game)
        text = "NEXT LEVEL" if self.game.current_level + 1 < self.game.max_levels else "MAIN MENU"
        self.next_btn = Button(game, WIDTH//2 - 90, 400, 180, 50, (0, 229, 255), text, 20, 10)

    def handle_click(self, pos):
        if self.next_btn.is_clicked(pos):
            if self.game.current_level + 1 < self.game.max_levels:
                self.game.next_level()
            else:
                self.game.change_state("MENU")

    def update(self):
        for e in self.game.physics.entities:
            if hasattr(e, 'update'):
                e.update()
        from constants import FPS
        self.game.physics.step(1.0 / FPS)

    def draw(self):
        draw_entities(self.game.screen, self.game.physics)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        self.game.screen.blit(overlay, (0, 0))
        
        txt = self.game.get_text("CLEARED!", 50, (255, 235, 59))
        txt_shadow = self.game.get_text("CLEARED!", 50, (31, 41, 55))
        self.game.screen.blit(txt_shadow, (WIDTH//2 - txt.get_width()//2 + 5, 205))
        self.game.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200))
        
        self.next_btn.draw(self.game.screen)
