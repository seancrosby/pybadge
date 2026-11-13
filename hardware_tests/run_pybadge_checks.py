"""Guided physical eBadge checks using the public ``pybadge`` API.

Run this file with mpremote after installing the hardware backend files. The
GPIO loopback check requires a jumper wire from GPIO13 to GPIO14. The analog
check requires a known voltage source and common ground. Use only the
documented GPIO voltage range and skip any setup that is unavailable.
"""

import pybadge


_results = []


def _record_check(name, action):
    """Run an action until it is passed, failed, or skipped."""
    while True:
        print("\n== {} ==".format(name))
        try:
            action()
        except pybadge.UnsupportedFeatureError as error:
            print("Skipped: {}".format(error))
            _results.append((name, "SKIP"))
            return
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


def _check_button(button, label):
    input("Hold {} and press Enter. ".format(label))
    pressed = pybadge.is_pressed(button)
    print("Pressed reading: {}".format(pressed))
    input("Release {} and press Enter. ".format(label))
    released = not pybadge.is_pressed(button)
    print("Released reading: {}".format(released))
    print("Both readings should be True.")


def _check_rgb_led():
    for color in ("red", "green", "blue"):
        pybadge.set_rgb_led(color)
        input("Confirm the RGB indicator appears {} and press Enter. ".format(color))
    pybadge.turn_rgb_led_off()


def _check_led_strip():
    colors = ["off"] * 24
    for index, color in enumerate(("red", "green", "blue")):
        colors[index] = color
    pybadge.set_led_strip(colors)
    input("Confirm strip LEDs 0–2 show red, green, and blue; press Enter. ")
    pybadge.clear_led_strip()


def _check_buzzer():
    input("A 440 Hz tone will play briefly. Press Enter to continue. ")
    pybadge.play_tone(440, 500)
    input("Did you hear the tone? Press Enter to record your result. ")


def _check_display():
    pybadge.display_clear(pybadge.BLUE)
    pybadge.display_text("eBadge hardware check", 8, 8, pybadge.WHITE)
    input("Confirm the blue screen and white text, then press Enter. ")
    pybadge.display_clear(pybadge.BLACK)


def _check_wifi():
    networks = pybadge.scan_wifi()
    print("Visible networks (SSID, RSSI dBm):")
    for network in networks:
        print("  {}".format(network))
    if not networks:
        print("No networks were returned; this may be normal in a shielded area.")


def _check_joystick():
    print("Move the joystick in all directions and verify normalized readings.")
    print("The hardware direction mapping is pending physical calibration.")
    pybadge.joystick()


def _check_gpio_loopback():
    print("Connect GPIO13 to GPIO14 with a jumper wire; connect no power source.")
    input("After checking the loopback wire, press Enter to run the check. ")
    pybadge.configure_pin(pybadge.GPIO13, mode="output")
    pybadge.configure_pin(pybadge.GPIO14, mode="input")
    try:
        pybadge.write_pin(pybadge.GPIO13, pybadge.HIGH)
        pybadge.pause(10)
        high_read = pybadge.is_high(pybadge.GPIO14)
        pybadge.write_pin(pybadge.GPIO13, pybadge.LOW)
        pybadge.pause(10)
        low_read = pybadge.is_low(pybadge.GPIO14)
    finally:
        pybadge.write_pin(pybadge.GPIO13, pybadge.LOW)
    print("HIGH loopback: {}; LOW loopback: {}".format(high_read, low_read))
    print("Both readings should be True.")


def _check_pwm():
    print("For a visible check, connect GPIO13 to an LED through a current-limiting resistor.")
    print("A scope or logic analyzer can also verify a 1 kHz, 50% waveform.")
    input("Connect a safe test load, or skip if unavailable; press Enter to continue. ")
    pybadge.configure_pin(pybadge.GPIO13, mode="output")
    try:
        pybadge.set_pwm(pybadge.GPIO13, frequency_hz=1000, duty_percent=50)
        input("Confirm the waveform or LED activity, then press Enter. ")
    finally:
        pybadge.stop_pwm(pybadge.GPIO13)
        pybadge.write_pin(pybadge.GPIO13, pybadge.LOW)


def _check_adc():
    print("Connect a known 1.5 V source to GPIO13 and its negative to board GND.")
    print("The ADC measurement range is approximately 0.15–2.45 V; GPIO max is 3.3 V.")
    print("ADC2 reads require Wi-Fi to be inactive. Do not connect an unknown source.")
    input("After checking the source and common ground, press Enter to measure. ")
    pybadge.configure_pin(pybadge.GPIO13, mode="input")
    measured = pybadge.read_voltage(pybadge.GPIO13)
    print("GPIO13 voltage: {:.3f} V".format(measured))
    input("Compare with your source or meter, then press Enter to record the result. ")


def _check_accelerometer():
    before = pybadge.read_accelerometer()
    print("Initial acceleration (g): {}".format(before))
    input("Tilt the badge, return it to rest, then press Enter. ")
    after = pybadge.read_accelerometer()
    print("After movement (g): {}".format(after))
    input("Confirm the values changed and press Enter to record the result. ")


def _check_battery_voltage():
    print("This reading requires the VMain-to-IO12 jumper bridge.")
    print("It is an uncalibrated estimate of the selected power rail, not battery charge.")
    input("If the jumper is installed and Wi-Fi is off, press Enter to read. ")
    voltage = pybadge.read_battery_voltage()
    print("Estimated selected-rail voltage: {:.3f} V".format(voltage))
    input("Compare with a meter if available, then press Enter to record. ")


def main():
    """Run each supported check and print a final result summary."""
    pybadge.initialize(mode="hardware")
    try:
        _record_check("Button A", lambda: _check_button(pybadge.BUTTON_A, "A"))
        _record_check("Button B", lambda: _check_button(pybadge.BUTTON_B, "B"))
        _record_check("Up button", lambda: _check_button(pybadge.BUTTON_UP, "Up"))
        _record_check("Down button", lambda: _check_button(pybadge.BUTTON_DOWN, "Down"))
        _record_check("Left button", lambda: _check_button(pybadge.BUTTON_LEFT, "Left"))
        _record_check("Right button", lambda: _check_button(pybadge.BUTTON_RIGHT, "Right"))
        _record_check("Joystick", _check_joystick)
        _record_check("RGB indicator", _check_rgb_led)
        _record_check("Addressable LED strip", _check_led_strip)
        _record_check("Buzzer", _check_buzzer)
        _record_check("Display", _check_display)
        _record_check("Wi-Fi scan", _check_wifi)
        _record_check("GPIO HIGH/LOW loopback", _check_gpio_loopback)
        _record_check("GPIO PWM", _check_pwm)
        _record_check("Analog voltage", _check_adc)
        _record_check("Accelerometer", _check_accelerometer)
        _record_check("Battery / selected-rail voltage", _check_battery_voltage)
    finally:
        pybadge.shutdown()

    print("\nHardware check summary:")
    for name, result in _results:
        print("{}: {}".format(result, name))


if __name__ == "__main__":
    main()
