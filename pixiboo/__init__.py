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
from .buttons import Buttons
from .buzzer import Buzzer
from .eyes import EyeLEDs

m = Matrix()
b = Buzzer()
e = EyeLEDs()
# Aliases for convenience
matrix = m
buzzer = b
eyes = e

__all__ = [
    "Matrix",
    "Buttons",
    "Buzzer",
    "EyeLEDs",
    "m",
    "b",
    "e",
    "matrix",
    "buzzer",
    "eyes",
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

