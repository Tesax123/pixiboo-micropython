"""
Comprehensive button demo showing all button APIs.

This example demonstrates:
1. on_button_pressed() - event-based callbacks (automatic, no update() needed!)
2. is_pressed() - immediate state check
3. Combining both approaches
"""

from pixiboo import *
import time

set_brightness(0.4)

# Color to cycle through when center button is pressed
current_color_idx = 0
colors = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE, PINK]

# Counter for left button presses
left_count = 0

# Define event handler functions
def on_left_button():
    """Called when left button is pressed."""
    global left_count
    left_count += 1
    print(f"Left pressed {left_count} times")
    
    # Flash left side of matrix
    for col in range(3):
        for row in range(7):
            m[row][col] = RED
    m.show()
    time.sleep(0.2)
    
    # Clear left side
    for col in range(3):
        for row in range(7):
            m[row][col] = BLACK
    m.show()

def on_center_button():
    """Called when center button is pressed."""
    global current_color_idx
    current_color_idx = (current_color_idx + 1) % len(colors)
    
    # Fill with next color
    m.fill(colors[current_color_idx])
    m.show()
    print(f"Color changed to: {current_color_idx}")
    
    # Play tone
    buzzer.tone(440 + (current_color_idx * 100), 100)

def on_right_button():
    """Called when right button is pressed."""
    print("Right button pressed!")
    
    # Flash right side of matrix
    for col in range(4, 7):
        for row in range(7):
            m[row][col] = BLUE
    m.show()
    time.sleep(0.2)
    
    # Clear right side
    for col in range(4, 7):
        for row in range(7):
            m[row][col] = BLACK
    m.show()

# Register the event handlers
on_button_pressed(Button.LEFT, on_left_button)
on_button_pressed(Button.CENTER, on_center_button)
on_button_pressed(Button.RIGHT, on_right_button)

print("Button demo running!")
print("Press buttons to trigger events")
print("Hold left + right together for special effect")

# Initial display
m.fill(colors[current_color_idx])
m.show()

# Main loop - events fire automatically, we just check for button combinations
while True:
    # Event callbacks fire automatically in the background!
    # We only need this loop to check for button combinations with is_pressed()
    
    # Use is_pressed() to check for button combinations
    # This runs every loop iteration (not debounced)
    if is_pressed(Button.LEFT) and is_pressed(Button.RIGHT):
        # Both buttons held - create a pattern
        m.fill(WHITE)
        m.show()
        # Note: Event callbacks still fire normally
    
    # Small delay to avoid consuming too much CPU
    time.sleep_ms(10)

