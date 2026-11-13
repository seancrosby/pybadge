"""Interactive checks for the underlying ``ebadge.py`` library.

This script is independent of ``pybadge.py``. Run it with mpremote after
copying ``ebadge.py``, ``board_v4.py``, the display driver, and font to the
badge. External GPIO checks require the physical setup described by each
prompt; use only 3.3 V logic.
"""

import machine
import ebadge


_results = []


def _check(name, action):
    while True:
        print("\n== {} ==".format(name))
        try:
            action()
        except Exception as error:
            print("The check raised {}: {}".format(type(error).__name__, error))

        choice = input("Record [p]ass, [f]ail, [r]etry, or [s]kip? ").strip().lower()
        if choice == "p":
            _results.append((name, "PASS"))
            return
        if choice == "f":
            _results.append((name, "FAIL"))
            return
        if choice == "s":
            _results.append((name, "SKIP"))
            return
        if choice != "r":
            print("Enter p, f, r, or s.")


def _button(button, label):
    input("Hold {} and press Enter. ".format(label))
    print("Pressed: {}".format(ebadge.is_pressed(button)))
    input("Release {} and press Enter. ".format(label))
    print("Released: {}".format(not ebadge.is_pressed(button)))


def _rgb_led():
    for color in (ebadge.RED, ebadge.GREEN, ebadge.BLUE):
        ebadge.set_led(color)
        input("Confirm RGB LED is {}, then press Enter. ".format(color))
    ebadge.turn_led_off()


def _led_strip():
    for index, color in enumerate((ebadge.RED, ebadge.GREEN, ebadge.BLUE)):
        ebadge.set_pixel(index, color)
    input("Confirm strip pixels 0–2 are red, green, and blue; press Enter. ")
    ebadge.clear_pixels()


def _display():
    ebadge.display_clear(ebadge.BLUE)
    ebadge.display_text("ebadge.py check", 8, 8, ebadge.WHITE)
    input("Confirm the blue screen and white text, then press Enter. ")
    ebadge.display_clear(ebadge.BLACK)


def _wifi():
    import network

    wlan = network.WLAN(network.STA_IF)
    was_active = wlan.active()
    if not was_active:
        wlan.active(True)
    try:
        found = wlan.scan()
    finally:
        if not was_active:
            wlan.active(False)
    for record in found:
        ssid, _bssid, _channel, rssi, _authmode, _hidden = record
        print("{}  {} dBm".format(ssid, rssi))
    if not found:
        print("No access points were returned.")


def _joystick():
    print("Raw joystick ADC readings: {}".format(ebadge.joystick()))
    input("Move the stick, return it to center, then press Enter. ")
    print("New raw readings: {}".format(ebadge.joystick()))


def _gpio_loopback():
    print("Connect GPIO13 to GPIO14 with a jumper wire; connect no power source.")
    input("Check the wire, then press Enter to continue. ")
    ebadge.configure_pin(13, mode="output")
    ebadge.configure_pin(14, mode="input")
    try:
        ebadge.write_pin(13, 1)
        high_read = ebadge.read_pin(14)
        ebadge.write_pin(13, 0)
        low_read = ebadge.read_pin(14)
    finally:
        ebadge.write_pin(13, 0)
    print("HIGH loopback: {}; LOW loopback: {}".format(high_read, low_read))


def _pwm():
    print("Connect GPIO13 to a scope or an LED through a current-limiting resistor.")
    input("Skip if you do not have a safe load; otherwise press Enter. ")
    pin = ebadge.configure_pin(13, mode="output")
    pwm = machine.PWM(pin, freq=1000, duty=512)
    try:
        input("Confirm 1 kHz, 50% PWM output, then press Enter. ")
    finally:
        pwm.duty(0)
        pwm.deinit()
        ebadge.write_pin(13, 0)


def _adc():
    print("Connect a known 1.5 V source to GPIO13 and its negative to board GND.")
    print("Keep the input within 0.15–2.45 V for the documented measurement range.")
    input("After checking the source and common ground, press Enter. ")
    pin = machine.Pin(13, machine.Pin.IN)
    adc = machine.ADC(pin)
    adc.atten(machine.ADC.ATTN_11DB)
    value = adc.read_uv() / 1000000.0
    print("GPIO13 voltage: {:.3f} V".format(value))
    input("Compare with your source or meter, then press Enter to record. ")


def _accelerometer():
    print("Initial acceleration (g): {}".format(ebadge.read_accelerometer()))
    input("Tilt the badge and return it to rest; press Enter. ")
    print("After movement (g): {}".format(ebadge.read_accelerometer()))


def _battery_raw():
    print("This reads raw ADC counts, not volts or a charge percentage.")
    print("It requires the VMain-to-IO12 jumper bridge.")
    input("If the jumper is installed and Wi-Fi is off, press Enter. ")
    print("Raw ADC count: {}".format(ebadge.read_battery()))


def main():
    ebadge.initialize()
    buttons = (
        (ebadge.button_a, "A"),
        (ebadge.button_b, "B"),
        (ebadge.button_up, "Up"),
        (ebadge.button_down, "Down"),
        (ebadge.button_left, "Left"),
        (ebadge.button_right, "Right"),
    )
    try:
        for button, label in buttons:
            _check("{} button".format(label), lambda b=button, n=label: _button(b, n))
        _check("Joystick", _joystick)
        _check("RGB indicator", _rgb_led)
        _check("Addressable LED strip", _led_strip)
        _check("Buzzer", lambda: ebadge.play_tone(440, 500))
        _check("Display", _display)
        _check("Wi-Fi scan", _wifi)
        _check("GPIO HIGH/LOW loopback", _gpio_loopback)
        _check("GPIO PWM", _pwm)
        _check("ADC voltage", _adc)
        _check("Accelerometer", _accelerometer)
        _check("Battery-sense raw ADC", _battery_raw)
    finally:
        ebadge.turn_led_off()
        ebadge.clear_pixels()
        ebadge.display_clear(ebadge.BLACK)

    print("\nHardware-library check summary:")
    for name, result in _results:
        print("{}: {}".format(result, name))


if __name__ == "__main__":
    main()
