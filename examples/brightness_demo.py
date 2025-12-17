import sys
import time

try:
    from pixiboo import *
except ImportError:
    for _p in ("..", "."):
        if _p not in sys.path:
            sys.path.insert(0, _p)
    from pixiboo import *

levels = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0]

while True:
    for level in levels:
        set_brightness(level)
        m.fill(BLUE)
        time.sleep(0.5)

