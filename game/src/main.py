import pygame
import sys
import json
import os
import math
from typing import Dict, Any
from physics import PhysicsWorld
from entities import Debris
import levels
from constants import WIDTH, HEIGHT, FPS
from states import MenuState, SelectState, PlayState, WinState

STATE_MAP = {
    "MENU": MenuState,
    "SELECT": SelectState,
    "PLAY": PlayState,
    "WIN": WinState
}

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Physics Box 2: Shield Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state_obj = None
        self.change_state("MENU")
        
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
        
        self.font_cache = {}
        self.text_cache = {}
        
    def get_font(self, size):
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.SysFont("Verdana", size, bold=True)
        return self.font_cache[size]
        
    def get_text(self, text, size, color):
        key = (text, size, color)
        if key not in self.text_cache:
            self.text_cache[key] = self.get_font(size).render(text, True, color)
        return self.text_cache[key]

    def load_settings(self) -> Dict[str, Any]:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading settings: {e}")
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
        self.change_state("PLAY")

    def change_state(self, state_name: str):
        if state_name in STATE_MAP:
            self.state_obj = STATE_MAP[state_name](self)

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
        if not isinstance(self.state_obj, STATE_MAP["WIN"]):
            self.change_state("WIN")
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
                self.state_obj.handle_click(event.pos)

    def update(self):
        self.state_obj.update()

    def draw(self):
        self.screen.fill((240, 244, 248)) 
        
        for y in range(0, HEIGHT, 50):
            for x in range(0, WIDTH, 30):
                dx = x if y % 100 == 0 else x + 15
                points = [(dx, y), (dx+8, y), (dx+8, y+16), (dx+4, y+20), (dx, y+16)]
                pygame.draw.polygon(self.screen, (226, 232, 240), points)

        self.state_obj.draw()
            
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
