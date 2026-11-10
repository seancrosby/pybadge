# Sweep a servo on GPIO 13 (minibadge CLK / spare IO). 50 Hz, 0.5–2.5 ms pulse.
import machine
import time

servo = machine.PWM(machine.Pin(13), freq=50)

def set_us(us):
    # duty_u16: 16-bit duty. period = 20000 us at 50 Hz.
    servo.duty_u16(int(us / 20000 * 65535))

while True:
    for us in range(500, 2500, 20):
        set_us(us)
        time.sleep_ms(15)
    for us in range(2500, 500, -20):
        set_us(us)
        time.sleep_ms(15)
