import pymunk

COLLISION_PLAYER = 1
COLLISION_GOAL = 2
COLLISION_WALL = 3
COLLISION_HAZARD = 4
COLLISION_SHIELD_ITEM = 5
COLLISION_PARTICLE = 6

class PhysicsWorld:
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, 980) 
        self.entities = []
        self.particles = []
        self.debris = []
        
        self.on_win = None
        self.on_death = None
        self.on_shield_pickup = None
        
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
        
    def draw(self, surface):
        for entity in self.entities:
            entity.draw(surface)
        for particle in self.particles:
            particle.draw(surface)
        for d in self.debris:
            d.draw(surface)
            
    def clear(self):
        for entity in self.entities:
            if hasattr(entity, 'body') and entity.body and hasattr(entity, 'shape') and entity.shape:
                self.space.remove(entity.body, entity.shape)
        for p in self.particles:
            self.space.remove(p.body, p.shape)
        for d in self.debris:
            self.space.remove(d.body, d.shape)
            
        self.entities.clear()
        self.particles.clear()
        self.debris.clear()
