import pymunk
from typing import List, Callable, Any, Optional
from constants import (
    COLLISION_PLAYER,
    COLLISION_GOAL,
    COLLISION_WALL,
    COLLISION_HAZARD,
    COLLISION_SHIELD_ITEM,
    COLLISION_PARTICLE
)

class PhysicsWorld:
    def __init__(self) -> None:
        self.space: pymunk.Space = pymunk.Space()
        self.space.gravity = (0, 980) 
        self.entities: List[Any] = []
        self.particles: List[Any] = []
        self.debris: List[Any] = []
        
        self.on_win: Optional[Callable[[], None]] = None
        self.on_death: Optional[Callable[[], None]] = None
        self.on_shield_pickup: Optional[Callable[[Any], None]] = None
        
        self.setup_handlers()
        
    def setup_handlers(self):
        self.space.on_collision(COLLISION_PLAYER, COLLISION_HAZARD, begin=self._handle_hazard)
        self.space.on_collision(COLLISION_PLAYER, COLLISION_SHIELD_ITEM, begin=self._handle_shield)
        self.space.on_collision(COLLISION_PLAYER, COLLISION_GOAL, begin=self._handle_goal)
        self.space.on_collision(None, None, begin=self._handle_particle)
        
    def _handle_hazard(self, arbiter, space, data):
        if self.on_death:
            self.on_death()
        arbiter.process_collision = False
        
    def _handle_shield(self, arbiter, space, data):
        shape = arbiter.shapes[1]
        if self.on_shield_pickup and hasattr(shape, 'entity'):
            # Must safely remove via post_step to avoid Pymunk locking errors
            space.add_post_step_callback(self._safely_remove_shield, shape.entity, shape.entity)
        arbiter.process_collision = False
        
    def _safely_remove_shield(self, space, key, entity):
        self.on_shield_pickup(entity)
        
    def _handle_goal(self, arbiter, space, data):
        if self.on_win:
            self.on_win()
        arbiter.process_collision = False
        
    def _handle_particle(self, arbiter, space, data):
        a, b = arbiter.shapes
        # Particles destroy on walls, but pass/bounce minimally from player/goal
        safe_types = [COLLISION_PLAYER, COLLISION_GOAL, COLLISION_SHIELD_ITEM, COLLISION_HAZARD]
        
        if a.collision_type == COLLISION_PARTICLE and b.collision_type not in safe_types:
            if hasattr(a, 'entity'):
                space.add_post_step_callback(self._safely_remove_particle, a.entity, a.entity)
        elif b.collision_type == COLLISION_PARTICLE and a.collision_type not in safe_types:
            if hasattr(b, 'entity'):
                space.add_post_step_callback(self._safely_remove_particle, b.entity, b.entity)
        arbiter.process_collision = True

    def _safely_remove_particle(self, space, key, particle):
        self.remove_particle(particle)

    def add_entity(self, entity):
        self.entities.append(entity)
        
    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
        if hasattr(entity, 'body') and entity.body and hasattr(entity, 'shape') and entity.shape:
            try:
                self.space.remove(entity.body, entity.shape)
            except AssertionError:
                pass

    def remove_particle(self, particle):
        if particle in self.particles:
            self.particles.remove(particle)
            try:
                self.space.remove(particle.body, particle.shape)
            except AssertionError:
                pass
            
    def step(self, dt):
        self.space.step(dt)
        
        for p in list(self.particles):
            if p.body.position.y > 1000 or p.body.position.x < -200 or p.body.position.x > 800:
                self.remove_particle(p)
                
        for d in list(self.debris):
            if d.body.position.y > 1000 or d.body.position.x < -200 or d.body.position.x > 800:
                self.debris.remove(d)
                try:
                    self.space.remove(d.body, d.shape)
                except AssertionError:
                    pass
        
    def clear(self):
        for entity in self.entities:
            if hasattr(entity, 'body') and entity.body and hasattr(entity, 'shape') and entity.shape:
                self.space.remove(entity.body, entity.shape)
        for p in self.particles:
            if hasattr(p, 'body') and p.body and hasattr(p, 'shape') and p.shape:
                self.space.remove(p.body, p.shape)
        for d in self.debris:
            if hasattr(d, 'body') and d.body and hasattr(d, 'shape') and d.shape:
                self.space.remove(d.body, d.shape)
            
        self.entities.clear()
        self.particles.clear()
        self.debris.clear()
