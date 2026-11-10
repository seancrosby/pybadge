# Popcorn melody on the piezo (GPIO 48). Copy board_v4.py + display libs to the board.
from board_v4 import *

C5, D5, E5, F5, G5, A5 = 523, 587, 659, 698, 784, 880
SIXTEENTH, DOTTED_EIGHTH, QUARTER, HALF = 63, 188, 250, 500
GAP_MS = 30

# Same notes as the Arduino popcorn demo, played at half speed.
MELODY = (
    (C5, SIXTEENTH), (C5, QUARTER), (C5, DOTTED_EIGHTH), (C5, SIXTEENTH),
    (C5, DOTTED_EIGHTH), (D5, SIXTEENTH), (E5, QUARTER), (F5, DOTTED_EIGHTH),
    (G5, SIXTEENTH), (A5, QUARTER), (D5, HALF), (G5, QUARTER),
    (G5, QUARTER), (G5, DOTTED_EIGHTH), (A5, SIXTEENTH), (G5, DOTTED_EIGHTH),
    (F5, SIXTEENTH), (E5, DOTTED_EIGHTH), (C5, SIXTEENTH), (D5, QUARTER),
    (C5, HALF),
)

tft_init(include_status_bar=False)
print("Popcorn")
print("Playing...")
while True:
    for freq, duration in MELODY:
        play_tone(freq, duration * 2)
        sleep(GAP_MS)
    sleep(800)
