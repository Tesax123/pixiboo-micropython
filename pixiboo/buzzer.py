"""
Simple buzzer wrapper for Pixiboo.
"""

from .hardware import BUZZER_PIN

try:
    from machine import Pin, PWM
except ImportError:  # pragma: no cover - host fallback
    class Pin:  # type: ignore
        OUT = 1

        def __init__(self, *_, **__):
            pass

    class PWM:  # type: ignore
        def __init__(self, *_args, **__):
            self._duty = 0

        def duty(self, value=None):
            if value is not None:
                self._duty = value
            return self._duty

        def freq(self, *_args, **__):
            return None

try:
    import utime as _time
except ImportError:  # pragma: no cover
    import time as _time


def _sleep_ms(ms: int) -> None:
    if hasattr(_time, "sleep_ms"):
        _time.sleep_ms(ms)  # type: ignore[attr-defined]
    else:
        _time.sleep(ms / 1000.0)


class Buzzer:
    def __init__(self):
        self._pwm = PWM(Pin(BUZZER_PIN))
        self._stopped = True

    def play(self, melody) -> None:
        """
        Play a melody defined as [(frequency, duration_ms), ...].
        If an entry is just a frequency, a 250 ms duration is used.
        """
        self._stopped = False
        for note in melody:
            if self._stopped:
                break
            if isinstance(note, (list, tuple)) and len(note) >= 2:
                freq, duration = note[0], note[1]
            else:
                freq, duration = note, 250
            self._pwm.freq(freq)
            self._pwm.duty(512)
            _sleep_ms(int(duration))
        self.stop()

    def stop(self) -> None:
        self._stopped = True
        self._pwm.duty(0)


__all__ = ["Buzzer"]

