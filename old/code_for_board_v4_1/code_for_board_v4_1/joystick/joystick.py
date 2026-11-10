# Read joystick X/Y ADC (GPIO 8 / 9) and print the 12-bit values.
import machine
from board_v4 import *

adc_x = machine.ADC(machine.Pin(8))
adc_y = machine.ADC(machine.Pin(9))
adc_x.atten(machine.ADC.ATTN_11DB)
adc_y.atten(machine.ADC.ATTN_11DB)
try:
    adc_x.width(machine.ADC.WIDTH_12BIT)
    adc_y.width(machine.ADC.WIDTH_12BIT)
except AttributeError:
    pass

tft_init(include_status_bar=False)
while True:
    x = adc_x.read()
    y = adc_y.read()
    tft.fill_rect(0, 40, DISPLAY_W, 80, st7789.BLACK)
    tft.text(font, "JOYSTICK", 8, 8, st7789.CYAN, st7789.BLACK)
    tft.text(font, "X: %d / 4095" % x, 8, 48, st7789.YELLOW, st7789.BLACK)
    tft.text(font, "Y: %d / 4095" % y, 8, 72, st7789.YELLOW, st7789.BLACK)
    sleep(80)
