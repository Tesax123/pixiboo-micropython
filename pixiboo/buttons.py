"""
Debounced access to Pixiboo buttons.
"""

from .hardware import BUTTON_LEFT, BUTTON_CENTER, BUTTON_RIGHT


class Button:
    """Button constants for event handlers."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

try:
    from machine import Pin
except ImportError:  # pragma: no cover - host fallback
    class Pin:  # type: ignore
        IN = 0
        PULL_UP = 2
        IRQ_FALLING = 2

        def __init__(self, *_, **__):
            pass

        def value(self):
            return 1
        
        def irq(self, *_, **__):
            pass

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
    def __init__(self, debounce_ms: int = 50, auto_update: bool = True):
        """
        Initialize button handling.
        
        Args:
            debounce_ms: Debounce time in milliseconds (default 50ms)
            auto_update: Automatically use interrupts for callbacks (default True)
        """
        self.debounce_ms = debounce_ms
        self.auto_update = auto_update
        self._pins = {
            "left": Pin(BUTTON_LEFT, Pin.IN, Pin.PULL_UP),
            "center": Pin(BUTTON_CENTER, Pin.IN, Pin.PULL_UP),
            "right": Pin(BUTTON_RIGHT, Pin.IN, Pin.PULL_UP),
        }
        self._last_state = {name: pin.value() for name, pin in self._pins.items()}
        now = _ticks_ms()
        self._last_time = {name: now for name in self._pins}
        self._callbacks = {name: [] for name in self._pins}
        self._irq_enabled = False

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

    def is_pressed(self, button: str) -> bool:
        """
        Check if a button is currently pressed (not debounced, immediate state).
        
        Args:
            button: Button name ("left", "center", or "right"), or Button.LEFT, Button.CENTER, Button.RIGHT
            
        Returns:
            True if button is currently pressed, False otherwise
        """
        if button not in self._pins:
            return False
        # In pull-up configuration, pressed = 0, not pressed = 1
        return self._pins[button].value() == 0

    def on_button_pressed(self, button: str, callback):
        """
        Register a callback function to be called when a button is pressed.
        
        Callbacks are automatically triggered using GPIO interrupts.
        
        Args:
            button: Button name ("left", "center", or "right"), or Button.LEFT, Button.CENTER, Button.RIGHT
            callback: Function to call when button is pressed (takes no arguments)
        
        Example:
            def on_left_pressed():
                print("Left button pressed!")
            
            buttons.on_button_pressed(Button.LEFT, on_left_pressed)
        """
        if button not in self._pins:
            return
        self._callbacks[button].append(callback)
        
        # Setup GPIO interrupts when first callback is registered
        if self.auto_update and not self._irq_enabled:
            self._setup_interrupts()
    
    def _setup_interrupts(self):
        """Setup GPIO interrupts for automatic button detection."""
        if self._irq_enabled:
            return
        
        try:
            # Setup interrupt for each button
            # Trigger on falling edge (button pressed with pull-up)
            for name, pin in self._pins.items():
                pin.irq(trigger=Pin.IRQ_FALLING, handler=self._make_irq_handler(name))
            
            self._irq_enabled = True
        except Exception as e:
            # If interrupts fail, user must call update() manually
            pass
    
    def _make_irq_handler(self, button_name: str):
        """Create an interrupt handler for a specific button."""
        def handler(pin):
            # Simple debounce check
            now = _ticks_ms()
            if _ticks_diff(now, self._last_time[button_name]) < self.debounce_ms:
                return  # Too soon, ignore
            
            self._last_time[button_name] = now
            
            # Call all registered callbacks for this button
            for callback in self._callbacks[button_name]:
                try:
                    callback()
                except Exception as e:
                    print(f"Error in button callback: {e}")
        
        return handler

    def update(self):
        """
        Check for button presses and call registered callbacks.
        
        Note: If auto_update is enabled (default), this is called automatically
        in the background and you don't need to call it manually.
        """
        for name in self._pins:
            if self._pressed(name):
                # Call all registered callbacks for this button
                for callback in self._callbacks[name]:
                    try:
                        callback()
                    except Exception:
                        # Don't let callback errors break the button system
                        pass


__all__ = ["Buttons", "Button"]

