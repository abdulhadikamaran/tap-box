import json
import os
from entities import Player, Wall, Goal, Hazard, ShieldItem, MovingPlatform

def load_level(level_idx, physics_world):
    physics_world.clear()
    
    level_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'levels', f'{level_idx}.json')
    if not os.path.exists(level_path):
        return None, None
        
    with open(level_path, 'r') as f:
        data = json.load(f)
        
    # JSON uses center-origin coordinates because it was ported directly from Matter.js config.
    # Our Entity wrapper classes (Wall, Hazard, Goal) expect top-left coordinate origin.
    # We apply transformations here dynamically.
    
    player = Player(physics_world, data['start']['x'], data['start']['y'])
    
    goal_w, goal_h = 40, 40
    goal = Goal(physics_world, data['goal']['x'] - goal_w//2, data['goal']['y'] - goal_h//2)
    
    for w in data.get('geometry', []):
        Wall(physics_world, w['x'] - w['w']//2, w['y'] - w['h']//2, w['w'], w['h'])
        
    for h in data.get('hazards', []):
        Hazard(physics_world, h['x'] - h['w']//2, h['y'] - h['h']//2, h['w'], h['h'])
        
    for m in data.get('moving', []):
        MovingPlatform(physics_world, m['x'] - m['w']//2, m['y'] - m['h']//2, m['w'], m['h'], m['axis'], m['min'], m['max'], m['speed'])
        
    for i in data.get('items', []):
        ShieldItem(physics_world, i['x'], i['y'])
        
    return player, goal
