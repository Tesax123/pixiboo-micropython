"""
Minimal button example.

This is as simple as it gets. No loops, no update() calls.
Just define what happens and register it.
"""

from pixiboo import *

def on_left():
    m.fill(RED)
    m.show()

def on_center():
    m.fill(GREEN)
    m.show()

def on_right():
    m.fill(BLUE)
    m.show()

# Register callbacks
on_button_pressed(Button.LEFT, on_left)
on_button_pressed(Button.CENTER, on_center)
on_button_pressed(Button.RIGHT, on_right)

# Initial display
m.fill(PURPLE)
m.show()

print("Press any button!")
# That's it! Program runs forever, callbacks fire automatically.

