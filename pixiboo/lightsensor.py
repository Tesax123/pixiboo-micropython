"""
Light sensor access for Pixiboo.

Reads ambient light level from the TEMT6000X01 phototransistor.
"""

from .hardware import LIGHT_SENSOR_PIN

try:
    from machine import ADC, Pin
except ImportError:  # pragma: no cover - host fallback
    class Pin:  # type: ignore
        pass

    class ADC:  # type: ignore
        def __init__(self, *_args, **__):
            self._value = 2048  # Simulate mid-range value

        def read(self):
            return self._value

        def read_u16(self):
            return self._value << 4  # Convert to 16-bit range


class LightSensor:
    """
    Light sensor interface for reading ambient light levels.
    
    The sensor returns values from 0 (dark) to 4095 (bright) on a 12-bit ADC.
    """

    def __init__(self):
        self._adc = ADC(Pin(LIGHT_SENSOR_PIN))

    def read(self) -> int:
        """
        Read the current light level.
        
        Returns:
            int: Light level from 0 (dark) to 4095 (bright)
        """
        return self._adc.read()

    def read_percent(self) -> float:
        """
        Read the current light level as a percentage.
        
        Returns:
            float: Light level from 0.0 (dark) to 100.0 (bright)
        """
        raw = self.read()
        return (raw / 4095.0) * 100.0


__all__ = ["LightSensor"]





