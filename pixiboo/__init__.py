"""
Pixiboo public API surface.

Only export the friendly symbols pupils use; hide hardware details.
"""

from .matrix import Matrix, set_brightness
from .colors import (
    BLACK,
    RED,
    GREEN,
    BLUE,
    WHITE,
    YELLOW,
    ORANGE,
    PURPLE,
    CYAN,
    PINK,
)
from .sprites import HEART
from .buttons import Buttons, Button
from .buzzer import Buzzer
from .eyes import EyeLEDs
from .accelerometer import Accelerometer, on_shake

m = Matrix()
b = Buzzer()
e = EyeLEDs()
buttons = Buttons()

# Don't auto-initialize accelerometer - it needs time to boot
# User must call init_accelerometer() or create Accelerometer() manually
accelerometer = None

def init_accelerometer():
    """
    Initialize the accelerometer (BNO055).
    
    Must be called after import if you want to use the accelerometer.
    The BNO055 can take up to 850ms to boot, so this is not done automatically.
    
    Returns:
        Accelerometer instance if successful, None if failed
    """
    global accelerometer
    try:
        accelerometer = Accelerometer()
        print("[Pixiboo] Accelerometer initialized successfully!")
        return accelerometer
    except Exception as err:
        print(f"[Pixiboo] Accelerometer initialization failed: {err}")
        accelerometer = None
        return None

# Helper functions for button events (delegates to buttons instance)
def on_button_pressed(button: str, callback):
    """
    Register a callback function to be called when a button is pressed.
    
    Args:
        button: Button name (Button.LEFT, Button.CENTER, or Button.RIGHT)
        callback: Function to call when button is pressed (takes no arguments)
    
    Example:
        def on_left():
            print("Left button pressed!")
        
        on_button_pressed(Button.LEFT, on_left)
    """
    buttons.on_button_pressed(button, callback)

def is_pressed(button: str) -> bool:
    """
    Check if a button is currently pressed.
    
    Args:
        button: Button name (Button.LEFT, Button.CENTER, or Button.RIGHT)
    
    Returns:
        True if button is currently pressed, False otherwise
    """
    return buttons.is_pressed(button)

# Aliases for convenience
matrix = m
buzzer = b
eyes = e

__all__ = [
    "Matrix",
    "Buttons",
    "Button",
    "Buzzer",
    "EyeLEDs",
    "Accelerometer",
    "m",
    "b",
    "e",
    "matrix",
    "buzzer",
    "eyes",
    "buttons",
    "accelerometer",
    "init_accelerometer",
    "on_button_pressed",
    "is_pressed",
    "on_shake",
    "set_brightness",
    "BLACK",
    "RED",
    "GREEN",
    "BLUE",
    "WHITE",
    "YELLOW",
    "ORANGE",
    "PURPLE",
    "CYAN",
    "PINK",
    "HEART",
]
