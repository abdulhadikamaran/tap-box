import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from physics import PhysicsWorld
import pymunk

def test_physics_world_init():
    pw = PhysicsWorld()
    assert isinstance(pw.space, pymunk.Space)
    assert pw.space.gravity == (0, 980)
    assert len(pw.entities) == 0

def test_physics_clear():
    class MockEntity:
        def __init__(self):
            self.body = None
            self.shape = None
            
    pw = PhysicsWorld()
    pw.particles.append(MockEntity())
    pw.clear()
    assert len(pw.particles) == 0

def test_on_shield_pickup():
    pw = PhysicsWorld()
    triggered = False
    
    def callback(entity):
        nonlocal triggered
        triggered = True
        
    pw.on_shield_pickup = callback
    pw.on_shield_pickup(None)
    assert triggered
