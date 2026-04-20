import json
import os
from typing import Tuple, Optional, Any
from entities import Player, Wall, Goal, Hazard, ShieldItem, MovingPlatform

def load_level(level_idx: int, physics_world: Any) -> Tuple[Optional[Player], Optional[Goal]]:
    physics_world.clear()
    
    level_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'levels', f'{level_idx}.json')
    if not os.path.exists(level_path):
        return None, None
        
    try:
        with open(level_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading level {level_idx}: {e}")
        return None, None
        
    start_pos = data.get('start', {'x': 200, 'y': 500})
    px = start_pos.get('x', 200)
    py = start_pos.get('y', 500)
    player = Player(physics_world, px, py)
    
    goal_pos = data.get('goal', {'x': 200, 'y': 50})
    gx = goal_pos.get('x', 200)
    gy = goal_pos.get('y', 50)
    goal_w, goal_h = 40, 40
    goal = Goal(physics_world, gx - goal_w//2, gy - goal_h//2)
    
    for item in data.get('geometry', []):
        if all(k in item for k in ('x', 'y', 'w', 'h')):
            Wall(physics_world, item['x'] - item['w']//2, item['y'] - item['h']//2, item['w'], item['h'])
        
    for item in data.get('hazards', []):
        if all(k in item for k in ('x', 'y', 'w', 'h')):
            Hazard(physics_world, item['x'] - item['w']//2, item['y'] - item['h']//2, item['w'], item['h'])
        
    for item in data.get('moving', []):
        if all(k in item for k in ('x', 'y', 'w', 'h', 'axis', 'min', 'max', 'speed')):
            MovingPlatform(physics_world, item['x'] - item['w']//2, item['y'] - item['h']//2, item['w'], item['h'], item['axis'], item['min'], item['max'], item['speed'])
        
    for item in data.get('items', []):
        if all(k in item for k in ('x', 'y')):
            ShieldItem(physics_world, item['x'], item['y'])

    return player, goal
