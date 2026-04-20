import pygame
import math
from typing import Any
from entities import Player, Wall, Goal, Hazard, ShieldItem, Particle, MovingPlatform, Debris
from constants import COL_WALL_FILL, COL_WALL_STROKE, COL_HAZARD_FILL, COL_HAZARD_STROKE

def draw_brutal_rect(surface: pygame.Surface, color: tuple, rect: Any, border_radius: int = 0) -> None:
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(*rect)
    shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.w, rect.h)
    pygame.draw.rect(surface, (31, 41, 55), shadow_rect, border_radius=border_radius)
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    pygame.draw.rect(surface, (31, 41, 55), rect, width=3, border_radius=border_radius)

def draw_brutal_circle(surface: pygame.Surface, color: tuple, center: tuple, radius: int) -> None:
    pygame.draw.circle(surface, (31, 41, 55), (center[0] + 4, center[1] + 4), radius)
    pygame.draw.circle(surface, color, center, radius)
    pygame.draw.circle(surface, (31, 41, 55), center, radius, width=3)

def draw_entities(surface: pygame.Surface, physics_world: Any) -> None:
    for entity in physics_world.entities:
        draw_entity(surface, entity)
    for p in physics_world.particles:
        draw_entity(surface, p)
    for d in physics_world.debris:
        draw_entity(surface, d)

def draw_player(surface: pygame.Surface, entity: Any) -> None:
    x, y = int(entity.body.position.x), int(entity.body.position.y)
    angle = entity.body.angle
    
    if entity.has_shield:
        pygame.draw.rect(surface, (224, 64, 251), (x - entity.size//2 - 4, y - entity.size//2 - 4, entity.size + 8, entity.size + 8), 4)

    rect_surf = pygame.Surface((entity.size, entity.size), pygame.SRCALPHA)
    pygame.draw.rect(rect_surf, (93, 64, 55), (0, 0, entity.size, entity.size), border_radius=4)
    pygame.draw.rect(rect_surf, (141, 110, 99), (3, 3, entity.size-6, entity.size-6), border_radius=2)
    
    font = pygame.font.SysFont("Arial", 20, bold=True)
    text = font.render("x", True, (215, 204, 200))
    text_rect = text.get_rect(center=(entity.size//2, entity.size//2 - 2))
    rect_surf.blit(text, text_rect)
    
    for p in [(5,5), (entity.size-5, 5), (5, entity.size-5), (entity.size-5, entity.size-5)]:
        pygame.draw.circle(rect_surf, (78, 52, 46), p, 2)
        
    rotated = pygame.transform.rotate(rect_surf, -math.degrees(angle))
    surface.blit(rotated, rotated.get_rect(center=(x, y)).topleft)

def draw_wall(surface: pygame.Surface, entity: Any) -> None:
    x = int(entity.body.position.x - entity.w//2)
    y = int(entity.body.position.y - entity.h//2)
    rect = pygame.Rect(x, y, entity.w, entity.h)
    pygame.draw.rect(surface, COL_WALL_FILL, rect)
    pygame.draw.rect(surface, COL_WALL_STROKE, rect, 4)

def draw_hazard(surface: pygame.Surface, entity: Any) -> None:
    x = int(entity.body.position.x - entity.w//2)
    y = int(entity.body.position.y - entity.h//2)
    rect = pygame.Rect(x, y, entity.w, entity.h)
    pygame.draw.rect(surface, COL_HAZARD_FILL, rect)
    pygame.draw.rect(surface, COL_HAZARD_STROKE, rect, 2)

def draw_goal(surface: pygame.Surface, entity: Any) -> None:
    x, y = int(entity.body.position.x - entity.w//2), int(entity.body.position.y - entity.h//2)
    pygame.draw.rect(surface, (84, 110, 122), (x + 18, y - 5, 4, 45))
    points = [(x + 20, y - 5), (x + 45, y + 5), (x + 20, y + 15)]
    pygame.draw.polygon(surface, (139, 195, 74), points)

def draw_shield(surface: pygame.Surface, entity: Any) -> None:
    x, y = int(entity.body.position.x), int(entity.body.position.y)
    pygame.draw.circle(surface, (213, 0, 249), (x, y), 10)
    pygame.draw.circle(surface, (255, 255, 255, 128), (x - 3, y - 3), 4)

def draw_particle(surface: pygame.Surface, entity: Any) -> None:
    x, y = int(entity.body.position.x), int(entity.body.position.y)
    pygame.draw.circle(surface, (93, 64, 55), (x, y), 9)
    pygame.draw.circle(surface, (141, 110, 99), (x, y), 7)

def draw_debris(surface: pygame.Surface, entity: Any) -> None:
    x, y = int(entity.body.position.x), int(entity.body.position.y)
    angle = entity.body.angle
    rect_surf = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.rect(rect_surf, (109, 76, 65), (0, 0, 14, 14))
    rotated = pygame.transform.rotate(rect_surf, -math.degrees(angle))
    surface.blit(rotated, rotated.get_rect(center=(x, y)).topleft)

RENDER_MAP = {
    Player: draw_player,
    Wall: draw_wall,
    MovingPlatform: draw_wall,
    Hazard: draw_hazard,
    Goal: draw_goal,
    ShieldItem: draw_shield,
    Particle: draw_particle,
    Debris: draw_debris
}

def draw_entity(surface: pygame.Surface, entity: Any) -> None:
    entity_type = type(entity)
    if entity_type in RENDER_MAP:
        RENDER_MAP[entity_type](surface, entity)
