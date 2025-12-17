"""
Debounced access to Pixiboo buttons.
"""

from .hardware import BUTTON_LEFT, BUTTON_CENTER, BUTTON_RIGHT

try:
    from machine import Pin
except ImportError:  # pragma: no cover - host fallback
    class Pin:  # type: ignore
        IN = 0
        PULL_UP = 2

        def __init__(self, *_, **__):
            pass

        def value(self):
            return 1

try:
    import utime as _time
except ImportError:  # pragma: no cover
    import time as _time


def _ticks_ms() -> int:
    if hasattr(_time, "ticks_ms"):
        return _time.ticks_ms()  # type: ignore[attr-defined]
    return int(_time.time() * 1000)


def _ticks_diff(a: int, b: int) -> int:
    if hasattr(_time, "ticks_diff"):
        return _time.ticks_diff(a, b)  # type: ignore[attr-defined]
    return a - b


class Buttons:
    def __init__(self, debounce_ms: int = 50):
        self.debounce_ms = debounce_ms
        self._pins = {
            "left": Pin(BUTTON_LEFT, Pin.IN, Pin.PULL_UP),
            "center": Pin(BUTTON_CENTER, Pin.IN, Pin.PULL_UP),
            "right": Pin(BUTTON_RIGHT, Pin.IN, Pin.PULL_UP),
        }
        self._last_state = {name: pin.value() for name, pin in self._pins.items()}
        now = _ticks_ms()
        self._last_time = {name: now for name in self._pins}

    def _pressed(self, name: str) -> bool:
        pin = self._pins[name]
        value = pin.value()
        now = _ticks_ms()
        if (
            value == 0
            and self._last_state[name] == 1
            and _ticks_diff(now, self._last_time[name]) >= self.debounce_ms
        ):
            self._last_state[name] = value
            self._last_time[name] = now
            return True
        self._last_state[name] = value
        self._last_time[name] = now
        return False

    def left_pressed(self) -> bool:
        return self._pressed("left")

    def center_pressed(self) -> bool:
        return self._pressed("center")

    def right_pressed(self) -> bool:
        return self._pressed("right")


__all__ = ["Buttons"]

