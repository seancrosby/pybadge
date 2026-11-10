# Cycle the RGB LED (GPIO 2/4/5).
from board_v4 import *

tft_init(include_status_bar=False)
print("RGB LED cycle")
colors = (RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, OFF)
i = 0
while True:
    set_rgb_color(colors[i])
    print("color", colors[i])
    i = (i + 1) % len(colors)
    sleep(400)
