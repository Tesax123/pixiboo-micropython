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
# from .accelerometer import Accelerometer
from .lightsensor import LightSensor

m = Matrix()
b = Buzzer()
e = EyeLEDs()
# a = Accelerometer()
l = LightSensor()
buttons = Buttons()
# Aliases for convenience
matrix = m
buzzer = b
eyes = e
# accelerometer = a
lightsensor = l


def on_button_pressed(button: str, callback):
    """
    Register a callback function to be called when a button is pressed.
    
    Callbacks run automatically in the background - no update() needed!
    
    Args:
        button: Button.LEFT, Button.CENTER, or Button.RIGHT
        callback: Function to call when button is pressed (takes no arguments)
    
    Example:
        from pixiboo import *
        
        def on_left_pressed():
            m.fill(RED)
            m.show()
        
        on_button_pressed(Button.LEFT, on_left_pressed)
        
        # That's it! The callback fires automatically when the button is pressed.
        # No need to call update() or have a while loop (unless you want one).
    """
    buttons.on_button_pressed(button, callback)


def is_pressed(button: str) -> bool:
    """
    Check if a button is currently pressed (immediate state, not debounced).
    
    Args:
        button: Button.LEFT, Button.CENTER, or Button.RIGHT
    
    Returns:
        True if button is currently pressed, False otherwise
        
    Example:
        from pixiboo import *
        
        while True:
            if is_pressed(Button.LEFT):
                print("Left button is pressed")
            time.sleep_ms(100)
    """
    return buttons.is_pressed(button)


def update():
    """
    Update the button system and call registered callbacks.
    
    NOTE: This is called automatically in the background when using on_button_pressed().
    You only need to call this manually if you disabled auto_update or want more control.
    
    Example (manual control):
        from pixiboo import *
        
        # Disable auto-update for manual control
        buttons.auto_update = False
        
        def on_left_pressed():
            m.fill(RED)
            m.show()
        
        on_button_pressed(Button.LEFT, on_left_pressed)
        
        while True:
            update()  # Manual update
            time.sleep_ms(10)
    """
    buttons.update()


__all__ = [
    "Matrix",
    "Buttons",
    "Button",
    "Buzzer",
    "EyeLEDs",
  # "Accelerometer",
    "LightSensor",
    "m",
    "b",
    "e",
  # "a",
    "l",
    "buttons",
    "matrix",
    "buzzer",
    "eyes",
  # "accelerometer",
    "lightsensor",
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
    "on_button_pressed",
    "is_pressed",
    "update",
]

