from pixiboo import *
import time

# Start in the center pixel (row 3, column 3)
row = 3
col = 3
colors = [RED, GREEN, BLUE, YELLOW]
color_idx = 0

set_brightness(0.4)
buttons = Buttons()

m[row][col] = colors[color_idx]
m.show()

while True:
    moved = False

    if buttons.left_pressed() and col > 0:
        col -= 1
        moved = True

    if buttons.right_pressed() and col < m.WIDTH - 1:
        col += 1
        moved = True

    if buttons.center_pressed():
        color_idx = (color_idx + 1) % len(colors)
        moved = True

    if moved:
        m.clear()
        m[row][col] = colors[color_idx]
        m.show()

    time.sleep_ms(50)
