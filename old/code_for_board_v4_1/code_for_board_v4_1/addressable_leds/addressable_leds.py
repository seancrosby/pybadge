# Light the 24 WS2812 LEDs on GPIO 7. Copy board_v4.py to the board.
from board_v4 import *

tft_init(include_status_bar=False)
print("Addressable LEDs")
addr_blank()
for i in range(NUM_ADDR_LEDS):
    px(i, RED if i % 3 == 0 else GREEN if i % 3 == 1 else BLUE)
addr_show()
while True:
    sleep(1000)
