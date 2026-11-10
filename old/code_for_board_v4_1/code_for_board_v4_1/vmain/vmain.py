# Read VMain / battery sense on GPIO 12.
# v4.0 divider is 150k/47k (x4.19, max ~6 V). v4.1 is 150k/10k (x16, max ~13 V).
import machine
from board_v4 import *

DIVIDER = 16.0           # v4.1 150k/10k divider
adc = machine.ADC(machine.Pin(12))
adc.atten(machine.ADC.ATTN_0DB)

tft_init(include_status_bar=False)
print("VMain / battery")
while True:
    raw = adc.read()
    v_pin = raw / 4095.0 * 2.0
    v_pwr = v_pin * DIVIDER
    tft.fill_rect(0, 40, DISPLAY_W, 60, st7789.BLACK)
    tft.text(font, "raw %d / 4095" % raw, 8, 48, st7789.WHITE, st7789.BLACK)
    tft.text(font, "%.2f V" % v_pwr, 8, 72, st7789.YELLOW, st7789.BLACK)
    sleep(200)
