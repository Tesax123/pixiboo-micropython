"""
Eye LED demo for Pixiboo.

Demonstrates controlling the left and right eye LEDs.
"""

from pixiboo import eyes

# Turn on both eyes
eyes.on()

# Wait a bit
import time
time.sleep(1)

# Turn off both eyes
eyes.off()
time.sleep(0.5)

# Turn on only left eye
eyes.left_on()
time.sleep(1)

# Turn on only right eye (left stays on)
eyes.right_on()
time.sleep(1)

# Turn off left eye
eyes.left_off()
time.sleep(1)

# Turn off right eye
eyes.right_off()
time.sleep(0.5)

# Toggle both eyes
eyes.toggle()
time.sleep(0.5)
eyes.toggle()
time.sleep(0.5)

# Blink both eyes
for _ in range(5):
    eyes.on()
    time.sleep(0.2)
    eyes.off()
    time.sleep(0.2)

# Alternating blink
for _ in range(5):
    eyes.left_on()
    eyes.right_off()
    time.sleep(0.2)
    eyes.left_off()
    eyes.right_on()
    time.sleep(0.2)

# Turn off at the end
eyes.off()

