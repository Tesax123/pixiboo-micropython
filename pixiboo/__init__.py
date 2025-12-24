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

m = Matrix()
b = Buzzer()
# Aliases for convenience
matrix = m
buzzer = b

__all__ = [
    "Matrix",
    "Buttons",
    "Buzzer",
    "m",
    "b",
    "matrix",
    "buzzer",
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

