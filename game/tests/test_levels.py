import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from levels import load_level

def test_load_level_missing():
    class MockPhysicsWorld:
        def clear(self):
            pass
            
    p, g = load_level(999, MockPhysicsWorld())
    assert p is None
    assert g is None
