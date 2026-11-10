# Blink the onboard LED on GPIO 6. Jumper silkscreen LED to IO6.
import machine
import time

led = machine.Pin(6, machine.Pin.OUT)
while True:
    led.value(1)
    time.sleep_ms(500)
    led.value(0)
    time.sleep_ms(500)
