"""
Move a pixel around using button callbacks!

Left button = move left
Right button = move right
Center button = change color
"""

from pixiboo import *

# Start in the center pixel
row = 3
col = 3
colors = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE, PINK]
color_idx = 0

set_brightness(0.4)

def update_display():
    """Redraw the pixel at current position."""
    m.clear()
    m[row][col] = colors[color_idx]
    m.show()

def on_left():
    """Move pixel left."""
    global col
    if col > 0:
        col -= 1
        update_display()

def on_right():
    """Move pixel right."""
    global col
    if col < m.WIDTH - 1:
        col += 1
        update_display()

def on_center():
    """Change color."""
    global color_idx
    color_idx = (color_idx + 1) % len(colors)
    update_display()

# Register the callbacks
on_button_pressed(Button.LEFT, on_left)
on_button_pressed(Button.RIGHT, on_right)
on_button_pressed(Button.CENTER, on_center)

# Show initial pixel
update_display()


