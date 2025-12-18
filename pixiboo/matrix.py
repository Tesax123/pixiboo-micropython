"""
Friendly 7x7 matrix wrapper for the Pixiboo board.
"""

from .colors import BLACK, RED
from .hardware import LED_PIN, NUM_LEDS

try:
    from machine import Pin
    import neopixel
except ImportError:  # pragma: no cover - host fallback
    class Pin:  # type: ignore
        IN = 0
        OUT = 1
        PULL_UP = 2

        def __init__(self, *_, **__):
            pass

        def value(self):
            return 1

    class _DummyNeoPixel:
        def __init__(self, *_args):
            self._buf = [(0, 0, 0)] * NUM_LEDS

        def __setitem__(self, idx, color):
            if 0 <= idx < len(self._buf):
                self._buf[idx] = color

        def write(self):
            pass

    class _DummyNeoModule:
        NeoPixel = _DummyNeoPixel

    neopixel = _DummyNeoModule()  # type: ignore

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


def _sleep_ms(ms: int) -> None:
    if hasattr(_time, "sleep_ms"):
        _time.sleep_ms(ms)  # type: ignore[attr-defined]
    else:
        _time.sleep(ms / 1000.0)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value


_default_brightness = 0.2


class _RowProxy:
    """
    Allows row-first access: m[row][column].
    """

    def __init__(self, matrix: "Matrix", y: int):
        self._matrix = matrix
        self._y = y

    def __getitem__(self, x: int):
        return self._matrix._get_pixel(x, self._y)

    def __setitem__(self, x: int, color):
        self._matrix._set_pixel(x, self._y, color)


class _NullRow:
    def __getitem__(self, _x):
        return BLACK

    def __setitem__(self, _x, _color):
        return None


class Matrix:
    WIDTH = 7
    HEIGHT = 7
    _instances = []

    def __init__(self):
        self._m = [[BLACK for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
        self.brightness = _default_brightness
        self._np = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)
        self._instances.append(self)

    def __getitem__(self, y: int):
        """
        Row-first indexing: m[row][column].
        """
        if 0 <= y < self.HEIGHT:
            return _RowProxy(self, y)
        return _NullRow()

    def __setitem__(self, y: int, value):
        # Allow m[row] = color to fill a row
        if 0 <= y < self.HEIGHT:
            for x in range(self.WIDTH):
                self._set_pixel(x, y, value)

    def _get_pixel(self, x: int, y: int):
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            return self._m[y][x]
        return BLACK

    def _set_pixel(self, x: int, y: int, color) -> None:
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            self._m[y][x] = color

    def _apply_brightness(self, color):
        return tuple(int(channel * self.brightness) for channel in color)

    def show(self) -> None:
        """
        Push the current buffer to the physical matrix.
        """
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                # Hardware is wired right-to-left; mirror the X axis so
                # m[row][column] matches visual left-to-right.
                x_hw = (self.WIDTH - 1) - x
                logical = y * self.WIDTH + x_hw
                physical = (NUM_LEDS - 1) - logical
                self._np[physical] = self._apply_brightness(self._m[y][x])
        self._np.write()

    def clear(self) -> None:
        self.fill(BLACK)

    def fill(self, color) -> None:
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                self._m[y][x] = color
        self.show()

    def draw(self, sprite, color=RED) -> None:
        # Centered draw; sprites are expected to be 7x7.
        sprite_height = len(sprite)
        sprite_width = len(sprite[0]) if sprite else 0
        offset_y = (self.HEIGHT - sprite_height) // 2
        offset_x = (self.WIDTH - sprite_width) // 2

        for sy, row in enumerate(sprite):
            for sx, ch in enumerate(row):
                if ch == "1":
                    self._set_pixel(offset_x + sx, offset_y + sy, color)
                else:
                    self._set_pixel(offset_x + sx, offset_y + sy, BLACK)
        self.show()

    def scroll_left(self, delay: int = 100) -> None:
        for y in range(self.HEIGHT):
            row = self._m[y]
            row.pop(0)
            row.append(BLACK)
        self.show()
        if delay:
            _sleep_ms(delay)

    def scroll_right(self, delay: int = 100) -> None:
        for y in range(self.HEIGHT):
            row = self._m[y]
            row.insert(0, BLACK)
            row.pop()
        self.show()
        if delay:
            _sleep_ms(delay)

    @property
    def brightness(self) -> float:
        return self._brightness

    @brightness.setter
    def brightness(self, value: float) -> None:
        self._brightness = _clamp(value)
        # Refresh hardware with new brightness
        if hasattr(self, "_np"):
            self.show()


def set_brightness(value: float) -> float:
    """
    Set brightness (0.0-1.0) for future matrices and update existing ones.
    """
    global _default_brightness
    _default_brightness = _clamp(value)
    for matrix in list(Matrix._instances):
        try:
            matrix.brightness = _default_brightness
        except Exception:
            # Keep going even if a stored matrix is unavailable
            pass
    return _default_brightness


__all__ = ["Matrix", "set_brightness"]

