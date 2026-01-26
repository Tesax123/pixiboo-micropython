"""
Rainbow Colors - Display all colors in a rainbow pattern

This example demonstrates:
- Setting individual pixels with different colors
- Using all available colors: RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE
- Creating a colorful display pattern
"""

from pixiboo import *

# Fill each row with a different color to create a rainbow effect
for i in range(7):
    m[0][i] = RED
    m[1][i] = ORANGE
    m[2][i] = YELLOW
    m[3][i] = GREEN
    m[4][i] = CYAN
    m[5][i] = BLUE
    m[6][i] = PURPLE

m.show()
