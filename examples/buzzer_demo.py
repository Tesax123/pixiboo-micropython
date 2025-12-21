from pixiboo import *
import time

m.clear()

# Simple rising then falling tones
melody = [
    (440, 200),  # A4
    (523, 200),  # C5
    (659, 200),  # E5
    (784, 300),  # G5
    (659, 200),
    (523, 200),
    (440, 400),
]

while True:
    b.play(melody)
    time.sleep_ms(1000)

