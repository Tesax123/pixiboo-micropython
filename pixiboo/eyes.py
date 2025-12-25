"""
Simple eye LED control for Pixiboo.
"""

from .hardware import EYE_LEFT_PIN, EYE_RIGHT_PIN

try:
    from machine import Pin
except ImportError:  # pragma: no cover - host fallback
    class Pin:  # type: ignore
        OUT = 1

        def __init__(self, *_, **__):
            self._value = 0

        def value(self, val=None):
            if val is not None:
                self._value = val
            return self._value


class EyeLEDs:
    """
    Control the left and right eye LEDs on the Pixiboo board.
    
    Simple on/off control for white LEDs.
    """

    def __init__(self):
        self._left_pin = Pin(EYE_LEFT_PIN, Pin.OUT)
        self._right_pin = Pin(EYE_RIGHT_PIN, Pin.OUT)
        # Start with both eyes off
        self.off()

    def left_on(self) -> None:
        """Turn on the left eye LED."""
        self._left_pin.value(1)

    def left_off(self) -> None:
        """Turn off the left eye LED."""
        self._left_pin.value(0)

    def right_on(self) -> None:
        """Turn on the right eye LED."""
        self._right_pin.value(1)

    def right_off(self) -> None:
        """Turn off the right eye LED."""
        self._right_pin.value(0)

    def on(self) -> None:
        """Turn on both eye LEDs."""
        self.left_on()
        self.right_on()

    def off(self) -> None:
        """Turn off both eye LEDs."""
        self.left_off()
        self.right_off()

    def toggle_left(self) -> None:
        """Toggle the left eye LED state."""
        self._left_pin.value(1 - self._left_pin.value())

    def toggle_right(self) -> None:
        """Toggle the right eye LED state."""
        self._right_pin.value(1 - self._right_pin.value())

    def toggle(self) -> None:
        """Toggle both eye LEDs."""
        self.toggle_left()
        self.toggle_right()


__all__ = ["EyeLEDs"]

