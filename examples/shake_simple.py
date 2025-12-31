"""
Simple shake detection demo.

Shows how to use the on_shake() entry point.
"""

from pixiboo import *

# Initialize accelerometer
init_accelerometer()

def on_shake_handler():
    """Called when device is shaken."""
    print("Shake detected!")
    matrix.fill(RED)
    matrix.show()
    buzzer.play([(880, 200)])

# Start shake monitoring
on_shake(on_shake_handler)

