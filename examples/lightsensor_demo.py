"""
Light sensor demo for Pixiboo.

Reads ambient light level and displays it on the matrix.
Brightness of the matrix corresponds to ambient light level.
"""

from pixiboo import *
import time

# Create light sensor instance
light = LightSensor()

while True:
    # Read light level (0-4095)
    level = light.read()
    
    # Convert to brightness (0.1 to 1.0)
    brightness = 0.1 + (level / 4095.0) * 0.9
    set_brightness(brightness)
    
    
    # Optional: Print light level for debugging
    print(f"Light level: {level} ({light.read_percent():.1f}%)")
    
    time.sleep(0.1)  # Update 10 times per second





