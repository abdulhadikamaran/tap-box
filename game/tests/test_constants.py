import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from constants import WIDTH, HEIGHT, FPS

def test_layout_constants():
    assert isinstance(WIDTH, int)
    assert isinstance(HEIGHT, int)
    assert isinstance(FPS, int)
    assert WIDTH > 0
    assert HEIGHT > 0
