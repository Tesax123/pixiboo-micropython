from pixiboo import *
import time

levels = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0]

while True:
    for level in levels:
        set_brightness(level)
        m.fill(BLUE)
        time.sleep(0.5)
