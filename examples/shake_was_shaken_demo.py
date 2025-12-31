"""
Shake detection demo using was_shaken() in a loop.

This example shows how to use was_shaken() to check for shakes
in your own loop, allowing you to combine it with other logic.
"""

from pixiboo import *
import time

# Initialize accelerometer
acc = init_accelerometer()

# Counter
shake_count = 0

print("Shake detection active!")
print("Shake the device to increment counter")
print("")

matrix.clear()
matrix.show()

while True:
    # Check if device was shaken
    if acc.was_shaken():
        shake_count += 1
        print(f"Shake #{shake_count}")
        
        # Flash the display
        matrix.fill(GREEN)
        matrix.show()
        time.sleep(0.1)
        matrix.clear()
        matrix.show()
        
        # Play a tone
        buzzer.play([(440 + (shake_count * 100), 100)])
    
    # Small delay
    time.sleep(0.05)

