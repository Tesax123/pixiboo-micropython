import sys

try:
    from pixiboo import *
except ImportError:
    for _p in ("..", "."):
        if _p not in sys.path:
            sys.path.insert(0, _p)
    from pixiboo import *

m.clear()
m.draw(HEART, RED)