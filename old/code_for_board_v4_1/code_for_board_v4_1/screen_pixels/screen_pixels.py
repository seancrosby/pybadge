# Draw colored boxes on the TFT.
from board_v4 import *

tft_init(include_status_bar=False)
tft.fill(st7789.BLACK)
tft.fill_rect(20, 20, 80, 80, st7789.RED)
tft.fill_rect(120, 20, 80, 80, st7789.GREEN)
tft.fill_rect(220, 20, 80, 80, st7789.BLUE)
tft.text(font, "pixels", 20, 120, st7789.WHITE, st7789.BLACK)
while True:
    sleep(1000)
