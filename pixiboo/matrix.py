"""
Friendly 7x7 matrix wrapper for the Pixiboo board.
"""

from .colors import BLACK, RED
from .hardware import LED_PIN, NUM_LEDS
from .font import get_char_pattern

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


# Default brightness: 0.8 (80% of the safe maximum)
# Note: We cap hardware brightness at 25% to prevent LED damage.
# User-facing brightness of 1.0 = 25% hardware brightness (maximum safe level)
# User-facing brightness of 0.8 = 20% hardware brightness (comfortable default)
_default_brightness = 0.8
_hardware_brightness_cap = 0.25  # Cap hardware at 25% to protect LEDs


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
        # Scale user brightness (0.0-1.0) to hardware brightness (0.0-0.25 max)
        # This protects the LEDs by capping at 25% hardware brightness
        hardware_brightness = self.brightness * _hardware_brightness_cap
        
        # Support both 3-tuple (R, G, B) and 4-tuple (R, G, B, per_pixel_brightness)
        if len(color) == 4:
            r, g, b, per_pixel_brightness = color
            # Apply per-pixel brightness multiplier, then global brightness
            pixel_brightness = hardware_brightness * _clamp(per_pixel_brightness, 0.0, 1.0)
            return (int(r * pixel_brightness), int(g * pixel_brightness), int(b * pixel_brightness))
        else:
            # Standard 3-tuple: apply global brightness only
            return tuple(int(channel * hardware_brightness) for channel in color)

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

    def display(self, text: str, color=RED, delay: int = 600) -> None:
        """
        Display characters of a string one by one with a flashing effect.
        Similar to micro:bit's display.show() behavior.
        
        Args:
            text: String to display character by character
            color: Color to display characters in (default: RED)
            delay: Milliseconds to show each character (default: 600ms)
        
        Example:
            m.display("HELLO")  # Shows H, then E, then L, then L, then O
        """
        for char in text:
            # Get the character pattern (7x7, uses full matrix)
            pattern = get_char_pattern(char)
            
            # Display the character
            for y, row in enumerate(pattern):
                for x, ch in enumerate(row):
                    if ch == "1":
                        self._set_pixel(x, y, color)
                    else:
                        self._set_pixel(x, y, BLACK)
            self.show()
            
            # Show character for delay milliseconds
            _sleep_ms(delay)
            
            # Clear the screen for flashing effect
            self.clear()
            _sleep_ms(100)  # Brief pause between characters

    @property
    def brightness(self) -> float:
        """
        Get the current brightness level (0.0 to 1.0).
        
        Note: For LED protection, brightness is capped at 25% hardware brightness.
        A user brightness of 1.0 equals 25% hardware brightness (maximum safe level).
        """
        return self._brightness

    @brightness.setter
    def brightness(self, value: float) -> None:
        """
        Set the brightness level (0.0 to 1.0).
        
        Args:
            value: Brightness from 0.0 (off) to 1.0 (maximum safe brightness)
        
        Note: For LED protection, the hardware is capped at 25% brightness.
        Setting brightness to 1.0 uses 25% hardware brightness (maximum safe level).
        """
        self._brightness = _clamp(value)
        # Refresh hardware with new brightness
        if hasattr(self, "_np"):
            self.show()


def set_brightness(value: float) -> float:
    """
    Set brightness (0.0-1.0) for future matrices and update existing ones.
    
    Args:
        value: Brightness from 0.0 (off) to 1.0 (maximum safe brightness)
    
    Returns:
        The clamped brightness value that was set
    
    Note: For LED protection, the hardware is capped at 25% brightness.
    Setting brightness to 1.0 uses 25% hardware brightness (maximum safe level).
    The default brightness is 0.8 (which equals 20% hardware brightness).
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


def set_grid(grid_data: list) -> None:
    """
    Set the entire matrix from a 7x7 grid of colors.
    This function preserves grid structure when converting between blocks and Python.
    
    Args:
        grid_data: A list of 7 lists, each containing 7 color values.
                   Example: [[BLACK, RED, BLACK, ...], [RED, RED, BLACK, ...], ...]
    """
    # Get the default matrix instance (usually 'm')
    if Matrix._instances:
        matrix = Matrix._instances[0]
        
        # Validate grid dimensions
        if len(grid_data) != Matrix.HEIGHT:
            raise ValueError(f"Grid must have {Matrix.HEIGHT} rows, got {len(grid_data)}")
        
        # Set each pixel from the grid data
        for y, row in enumerate(grid_data):
            if len(row) != Matrix.WIDTH:
                raise ValueError(f"Row {y} must have {Matrix.WIDTH} columns, got {len(row)}")
            for x, color in enumerate(row):
                matrix._set_pixel(x, y, color)
        
        # Show the grid on the matrix
        matrix.show()
    else:
        # No matrix instance exists yet - this is okay, the grid will be applied when matrix is created
        pass


__all__ = ["Matrix", "set_brightness", "set_grid"]

