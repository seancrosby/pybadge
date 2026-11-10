# Show which of the six buttons are pressed. Copy board_v4.py + display libs to the board.
from board_v4 import *

tft_init(include_status_bar=False)
names = (("A", button_A), ("B", button_B), ("Up", button_up),
         ("Down", button_down), ("Left", button_left), ("Right", button_right))

while True:
    tft.fill_rect(0, 0, DISPLAY_W, DISPLAY_H, st7789.BLACK)
    tft.text(font, "BUTTONS", 8, 8, st7789.CYAN, st7789.BLACK)
    y = 40
    for name, pin in names:
        pressed = is_pressed(pin)
        tft.text(font, name + ": " + ("HIGH" if pressed else "LOW"), 8, y,
                 st7789.RED if pressed else st7789.WHITE, st7789.BLACK)
        y += 24
    sleep(100)
