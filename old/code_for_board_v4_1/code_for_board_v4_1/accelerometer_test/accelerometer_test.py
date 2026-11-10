# Read the MMA8452 on I2C (SDA 41, SCL 42) and print X/Y/Z.
import machine
from board_v4 import *

tft_init(include_status_bar=False)
i2c = machine.I2C(0, scl=machine.Pin(42), sda=machine.Pin(41), freq=400000)
ADDR = 0x1C
if ADDR in i2c.scan():
    i2c.writeto_mem(ADDR, 0x2A, bytes([0x01]))  # CTRL_REG1 active
    print("MMA8452 OK")
else:
    print("No accelerometer")

def read_axis(reg):
    raw = i2c.readfrom_mem(ADDR, reg, 2)
    val = (raw[0] << 4) | (raw[1] >> 4)
    if val & 0x800:
        val -= 0x1000
    return val / 1024.0

while True:
    if ADDR in i2c.scan():
        x, y, z = read_axis(0x01), read_axis(0x03), read_axis(0x05)
        tft.fill_rect(0, 40, DISPLAY_W, 80, st7789.BLACK)
        tft.text(font, "X: %.2f g" % x, 8, 48, st7789.YELLOW, st7789.BLACK)
        tft.text(font, "Y: %.2f g" % y, 8, 72, st7789.YELLOW, st7789.BLACK)
        tft.text(font, "Z: %.2f g" % z, 8, 96, st7789.YELLOW, st7789.BLACK)
    sleep(150)
