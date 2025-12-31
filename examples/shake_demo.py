"""
Shake detection demo with button handlers.

This example shows how on_shake() and on_button_pressed() work together.
Buttons use GPIO interrupts, so they fire even while on_shake() is running.
"""

from pixiboo import *
import time

# Initialize accelerometer
init_accelerometer()

# Counter for shake events
shake_count = 0

# Current color
current_color = RED

def handle_left_button():
    """Left button changes color to RED."""
    global current_color
    current_color = RED
    print("Color changed to RED")
    matrix.fill(RED)
    matrix.show()
    buzzer.play([(440, 100)])

def handle_center_button():
    """Center button changes color to GREEN."""
    global current_color
    current_color = GREEN
    print("Color changed to GREEN")
    matrix.fill(GREEN)
    matrix.show()
    buzzer.play([(523, 100)])

def handle_right_button():
    """Right button changes color to BLUE."""
    global current_color
    current_color = BLUE
    print("Color changed to BLUE")
    matrix.fill(BLUE)
    matrix.show()
    buzzer.play([(659, 100)])

def handle_shake():
    """Called when device is shaken."""
    global shake_count
    shake_count += 1
    
    print(f"Shake detected! Count: {shake_count}")
    
    # Flash the current color
    matrix.fill(current_color)
    matrix.show()
    time.sleep(0.1)
    matrix.clear()
    matrix.show()
    time.sleep(0.1)
    matrix.fill(current_color)
    matrix.show()
    
    # Play a sound effect
    buzzer.play([(880, 50), (1047, 50), (1319, 50)])

# Register button handlers (these use GPIO interrupts - work asynchronously)
on_button_pressed(Button.LEFT, handle_left_button)
on_button_pressed(Button.CENTER, handle_center_button)
on_button_pressed(Button.RIGHT, handle_right_button)

# Initial display
print("Shake Demo Ready!")
print("Press buttons to change colors:")
print("  LEFT = RED")
print("  CENTER = GREEN")
print("  RIGHT = BLUE")
print("Shake the device to trigger flash effect!")
print("")

matrix.fill(current_color)
matrix.show()

# Start shake monitoring (this blocks, but button interrupts still work!)
on_shake(handle_shake, threshold_mg=1500)

