import sys
sys.path.insert(0, r"C:\Users\tessa\OneDrive\Bureaublad\microbitcharmthing\technical_process\micropython\pixiboo-micropython")
from pixiboo import *

set_brightness(0.3)
m.clear()
m[3][3] = BLUE
m.show()
