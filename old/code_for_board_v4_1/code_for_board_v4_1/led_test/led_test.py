# Cycle the RGB LED, then a chase on the 24 addressable LEDs.
from board_v4 import *

tft_init(include_status_bar=False)
print("LED test")
print("RGB, then ring")

colors = (RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE)

while True:
    for color in colors:
        set_rgb_color(color)
        sleep(350)
    rgb_off()
    addr_blank()
    for i in range(NUM_ADDR_LEDS):
        addr_blank()
        px(i, GREEN)
        addr_show()
        sleep(40)
    addr_blank()
    addr_show()
    sleep(400)
