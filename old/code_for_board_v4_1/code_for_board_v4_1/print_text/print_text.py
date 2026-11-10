# Print text on the ST7789 TFT.
from board_v4 import *

tft_init(include_status_bar=False)
print("Hello, e-Badge!")
print("MicroPython on v4")
print("B = not used")
while True:
    sleep(1000)
