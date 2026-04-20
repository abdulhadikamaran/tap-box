import pygame
import pymunk
import math
import random
from physics import *

# Colors mapped from original HTML
COL_WALL_FILL = (144, 164, 174)
COL_WALL_STROKE = (69, 90, 100)
COL_HAZARD_FILL = (224, 64, 251)
COL_HAZARD_STROKE = (170, 0, 255)

class Entity:
    def __init__(self, physics_world):
        self.pw = physics_world
        self.body = None
        self.shape = None
        
    def setup(self):
        if self.body and self.shape:
            self.pw.space.add(self.body, self.shape)
        self.pw.add_entity(self)

    def draw(self, surface):
        pass

class Player(Entity):
    def __init__(self, physics_world, x, y):
        super().__init__(physics_world)
        self.size = 35
        mass = 1.0
        moment = pymunk.moment_for_box(mass, (self.size, self.size))
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        self.shape = pymunk.Poly.create_box(self.body, (self.size, self.size))
        self.shape.friction = 0.5
        self.shape.elasticity = 0.2
        self.shape.collision_type = COLLISION_PLAYER
        self.has_shield = False
        self.setup()

    def apply_recoil(self, angle, force=400):
        fx = -math.cos(angle) * force
        fy = -math.sin(angle) * force
        self.body.apply_impulse_at_local_point((fx, fy), (0,0)) # Apply to center

    def draw(self, surface):
        x, y = int(self.body.position.x), int(self.body.position.y)
        angle = self.body.angle
        
        # Shield Glow Effect
        if self.has_shield:
            pygame.draw.rect(surface, (224, 64, 251), (x - self.size//2 - 4, y - self.size//2 - 4, self.size + 8, self.size + 8), 4)

        rect_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(rect_surf, (93, 64, 55), (0, 0, self.size, self.size), border_radius=4)
        pygame.draw.rect(rect_surf, (141, 110, 99), (3, 3, self.size-6, self.size-6), border_radius=2)
        
        font = pygame.font.SysFont("Arial", 20, bold=True)
        text = font.render("x", True, (215, 204, 200))
        text_rect = text.get_rect(center=(self.size//2, self.size//2 - 2))
        rect_surf.blit(text, text_rect)
        
        # Four bolts
        pygame.draw.circle(rect_surf, (78, 52, 46), (5, 5), 2)
        pygame.draw.circle(rect_surf, (78, 52, 46), (self.size-5, 5), 2)
        pygame.draw.circle(rect_surf, (78, 52, 46), (5, self.size-5), 2)
        pygame.draw.circle(rect_surf, (78, 52, 46), (self.size-5, self.size-5), 2)
        
        rotated_surf = pygame.transform.rotate(rect_surf, -math.degrees(angle))
        new_rect = rotated_surf.get_rect(center=(x, y))
        surface.blit(rotated_surf, new_rect.topleft)

class Wall(Entity):
    def __init__(self, physics_world, x, y, w, h):
        super().__init__(physics_world)
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (x + w//2, y + h//2)
        self.shape = pymunk.Poly.create_box(self.body, (w, h))
        self.shape.friction = 0.5
        self.shape.elasticity = 0.1
        self.shape.collision_type = COLLISION_WALL
        self.w = w
        self.h = h
        self.setup()

    def draw(self, surface):
        x = int(self.body.position.x - self.w//2)
        y = int(self.body.position.y - self.h//2)
        rect = pygame.Rect(x, y, self.w, self.h)
        pygame.draw.rect(surface, COL_WALL_FILL, rect)
        pygame.draw.rect(surface, COL_WALL_STROKE, rect, 4)

class Goal(Entity):
    def __init__(self, physics_world, x, y):
        super().__init__(physics_world)
        self.w, self.h = 40, 40
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (x + self.w//2, y + self.h//2)
        self.shape = pymunk.Poly.create_box(self.body, (self.w, self.h))
        self.shape.sensor = True
        self.shape.collision_type = COLLISION_GOAL
        self.setup()

    def draw(self, surface):
        x, y = int(self.body.position.x - self.w//2), int(self.body.position.y - self.h//2)
        pygame.draw.rect(surface, (84, 110, 122), (x + 18, y - 5, 4, 45))
        points = [(x + 20, y - 5), (x + 45, y + 5), (x + 20, y + 15)]
        pygame.draw.polygon(surface, (139, 195, 74), points)

class Hazard(Entity):
    def __init__(self, physics_world, x, y, w, h):
        super().__init__(physics_world)
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (x + w//2, y + h//2)
        self.shape = pymunk.Poly.create_box(self.body, (w, h))
        self.shape.collision_type = COLLISION_HAZARD
        self.w = w
        self.h = h
        self.setup()

    def draw(self, surface):
        x = int(self.body.position.x - self.w//2)
        y = int(self.body.position.y - self.h//2)
        rect = pygame.Rect(x, y, self.w, self.h)
        pygame.draw.rect(surface, COL_HAZARD_FILL, rect)
        pygame.draw.rect(surface, COL_HAZARD_STROKE, rect, 2)

class ShieldItem(Entity):
    def __init__(self, physics_world, x, y):
        super().__init__(physics_world)
        self.r = 12
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, self.r)
        self.shape.sensor = True
        self.shape.collision_type = COLLISION_SHIELD_ITEM
        self.shape.entity = self
        self.setup()

    def draw(self, surface):
        x, y = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(surface, (213, 0, 249), (x, y), 10)
        pygame.draw.circle(surface, (255, 255, 255, 128), (x - 3, y - 3), 4)

class Particle:
    def __init__(self, physics_world, x, y, angle):
        self.pw = physics_world
        self.r = 9
        mass = 0.5
        moment = pymunk.moment_for_circle(mass, 0, self.r)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        speed = 500
        self.body.velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
        
        self.shape = pymunk.Circle(self.body, self.r)
        self.shape.sensor = True
        self.shape.collision_type = COLLISION_PARTICLE
        self.shape.entity = self
        
        self.pw.space.add(self.body, self.shape)
        self.pw.particles.append(self)

    def draw(self, surface):
        x, y = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(surface, (93, 64, 55), (x, y), 9)
        pygame.draw.circle(surface, (141, 110, 99), (x, y), 7)

class MovingPlatform(Entity):
    def __init__(self, physics_world, x, y, w, h, axis, _min, _max, speed):
        super().__init__(physics_world)
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = (x + w//2, y + h//2)
        self.shape = pymunk.Poly.create_box(self.body, (w, h))
        self.shape.friction = 0.5
        self.shape.collision_type = COLLISION_WALL
        self.w = w
        self.h = h
        self.axis = axis
        self.min = _min + (w//2 if axis=='x' else h//2)
        self.max = _max + (w//2 if axis=='x' else h//2)
        self.speed = speed
        self.dir = 1
        self.setup()

    def update(self):
        pos = self.body.position
        if self.axis == 'x':
            if pos.x >= self.max or pos.x <= self.min:
                self.dir *= -1
            self.body.velocity = (self.speed * self.dir * 60, 0)
        else:
            if pos.y >= self.max or pos.y <= self.min:
                self.dir *= -1
            self.body.velocity = (0, self.speed * self.dir * 60)

    def draw(self, surface):
        x = int(self.body.position.x - self.w//2)
        y = int(self.body.position.y - self.h//2)
        rect = pygame.Rect(x, y, self.w, self.h)
        pygame.draw.rect(surface, COL_WALL_FILL, rect)
        pygame.draw.rect(surface, COL_WALL_STROKE, rect, 4)

class Debris:
    def __init__(self, physics_world, x, y):
        self.pw = physics_world
        size = 14
        mass = 0.2
        moment = pymunk.moment_for_box(mass, (size, size))
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        self.body.velocity = ((random.random()-0.5) * 600, (random.random()-0.5) * 600 - 200)
        
        self.shape = pymunk.Poly.create_box(self.body, (size, size))
        self.shape.friction = 0.5
        self.shape.filter = pymunk.ShapeFilter(categories=0b10, mask=0b01) # only collide with walls
        self.shape.collision_type = COLLISION_PARTICLE
        
        self.pw.space.add(self.body, self.shape)
        self.pw.debris.append(self)

    def draw(self, surface):
        x, y = int(self.body.position.x), int(self.body.position.y)
        angle = self.body.angle
        rect_surf = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.rect(rect_surf, (109, 76, 65), (0, 0, 14, 14))
        
        rotated = pygame.transform.rotate(rect_surf, -math.degrees(angle))
        rect = rotated.get_rect(center=(x, y))
        surface.blit(rotated, rect.topleft)
