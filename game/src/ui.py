import pygame
from renderer import draw_brutal_rect
from typing import Tuple, Any

class Button:
    def __init__(self, game: Any, x: int, y: int, w: int, h: int, color: Tuple[int, int, int], 
                 text: str = "", font_size: int = 14, radius: int = 0, 
                 text_color: Tuple[int, int, int] = (31, 41, 55),
                 click_sound: Any = None):
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.font_size = font_size
        self.radius = radius
        self.text_color = text_color
        self.click_sound = click_sound

    def draw(self, surface: pygame.Surface) -> None:
        draw_brutal_rect(surface, self.color, self.rect, self.radius)
        if self.text:
            txt_surf = self.game.get_text(self.text, self.font_size, self.text_color)
            cx = self.rect.x + self.rect.w // 2 - txt_surf.get_width() // 2
            cy = self.rect.y + self.rect.h // 2 - txt_surf.get_height() // 2
            surface.blit(txt_surf, (cx, cy))

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        if self.rect.collidepoint(pos):
            if self.click_sound:
                self.click_sound.play()
            else:
                self.game.snd_click.play()
            return True
        return False
