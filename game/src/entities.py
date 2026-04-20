import pygame
import pymunk
import math
import random
from typing import Any
from constants import (
    COLLISION_PLAYER,
    COLLISION_GOAL,
    COLLISION_WALL,
    COLLISION_HAZARD,
    COLLISION_SHIELD_ITEM,
    COLLISION_PARTICLE,
    COL_WALL_FILL,
    COL_WALL_STROKE,
    COL_HAZARD_FILL,
    COL_HAZARD_STROKE
)

class Entity:
    def __init__(self, physics_world: Any) -> None:
        self.pw = physics_world
        self.body = None
        self.shape = None
        
    def setup(self):
        if self.body and self.shape:
            self.pw.space.add(self.body, self.shape)
        self.pw.add_entity(self)

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
        self.body.apply_impulse_at_local_point((fx, fy), (0,0))

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

