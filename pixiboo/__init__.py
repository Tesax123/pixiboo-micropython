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
)
from .sprites import HEART
from .buttons import Buttons

m = Matrix()

__all__ = [
    "Matrix",
    "Buttons",
    "m",
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
    "HEART",
]

