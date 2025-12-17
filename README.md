# Pixiboo MicroPython Library

Friendly 7x7 matrix helper for the Pixiboo classroom device. Pupils interact with a tiny API that hides pins, NeoPixel setup, and RGB tuples.

## Installation (via mip)

```python
import mip
mip.install("github:tessaract/pixiboo-micropython")
```

## Quick start

```python
from pixiboo import Matrix, BLUE, HEART, set_brightness

m = Matrix()
set_brightness(0.3)

m.clear()
m[3][3] = BLUE

m.draw(HEART)
m.scroll_left()
```

## Supported hardware

- Pixiboo 7x7 board using `LED_PIN=18`, `NUM_LEDS=49`
- Buttons on pins 12/11/13 (left/center/right)
- Buzzer on pin 38

## Freezing Pixiboo into firmware (later)

Freezing bundles the library into the device firmware so lessons start instantly without installing files at the REPL. Pixiboo will use freezing to:

- Ship a ready-to-use Matrix API on fresh devices
- Reduce classroom setup time and avoid storage wear
- Keep the API version consistent across devices

High-level steps (no commands yet):

1. Build MicroPython firmware with Pixiboo sources included.
2. Freeze the `pixiboo` package and example files into the firmware image.
3. Flash the image onto devices used in class.
4. Smoke-test `import pixiboo` and a simple pixel set to confirm success.

## Examples

- `examples/hello_pixel.py` — set one pixel
- `examples/draw_heart.py` — draw the heart sprite
- `examples/brightness_demo.py` — cycle brightness

