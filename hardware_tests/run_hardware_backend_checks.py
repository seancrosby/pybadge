"""Interactive checks of the maintained hardware backend implementation."""

from pybadge import UnsupportedFeatureError
from backends.hardware_backend import HardwareBackend


_backend = None
_results = []


def _check(name, action):
    """Run an interactive check and record its result."""
    while True:
        print("\n== {} ==".format(name))
        try:
            action()
        except UnsupportedFeatureError as error:
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


def _button(button, label):
    input("Hold {} and press Enter. ".format(label))
    print("Pressed: {}".format(_backend.is_pressed(button)))
    input("Release {} and press Enter. ".format(label))
    print("Released: {}".format(not _backend.is_pressed(button)))


def _rgb_led():
    for color in ("red", "green", "blue"):
        _backend.set_rgb_led(color)
        input("Confirm RGB LED is {}, then press Enter. ".format(color))
    _backend.turn_rgb_led_off()


def _led_strip():
    for index, color in enumerate(("red", "green", "blue")):
        _backend.set_led_strip_pixel(index, color)
    input("Confirm strip pixels 0–2 are red, green, and blue; press Enter. ")
    _backend.clear_led_strip()


def _display():
    _backend.display_clear("blue")
    _backend.display_text("Hardware backend check", 8, 8, "white")
    input("Confirm the blue screen and white text, then press Enter. ")
    _backend.display_clear("black")


def _wifi():
    results = _backend.scan_wifi()
    for ssid, signal_dbm in results:
        print("{}  {} dBm".format(ssid, signal_dbm))
    if not results:
        print("No access points were returned.")


def _joystick():
    print("Move the joystick and verify its normalized direction readings.")
    _backend.joystick()


def _gpio_loopback():
    print("Connect GPIO13 to GPIO14 with a jumper wire; connect no power source.")
    input("Check the wire, then press Enter to continue. ")
    _backend.configure_pin(13, "output", None)
    _backend.configure_pin(14, "input", None)
    try:
        _backend.write_pin(13, 1)
        high_read = bool(_backend.read_pin(14))
        _backend.write_pin(13, 0)
        low_read = not bool(_backend.read_pin(14))
    finally:
        _backend.write_pin(13, 0)
    print("HIGH loopback: {}; LOW loopback: {}".format(high_read, low_read))


def _pwm():
    print("Connect GPIO13 to a scope or an LED through a current-limiting resistor.")
    input("Skip if you do not have a safe load; otherwise press Enter. ")
    _backend.configure_pin(13, "output", None)
    try:
        _backend.set_pwm(13, 1000, 50)
        input("Confirm 1 kHz, 50% PWM output, then press Enter. ")
    finally:
        _backend.stop_pwm(13)
        _backend.write_pin(13, 0)


def _adc():
    print("Connect a known 1.5 V source to GPIO13 and its negative to board GND.")
    print("Keep the input within the documented ADC measurement range.")
    input("After checking the source and common ground, press Enter. ")
    _backend.configure_pin(13, "input", None)
    print("GPIO13 voltage: {:.3f} V".format(_backend.read_voltage(13)))
    input("Compare with your source or meter, then press Enter to record. ")


def _accelerometer():
    print("Initial acceleration (g): {}".format(_backend.read_accelerometer()))
    input("Tilt the badge and return it to rest; press Enter. ")
    print("After movement (g): {}".format(_backend.read_accelerometer()))


def _battery_voltage():
    print("This estimate requires the VMain-to-IO12 jumper and Wi-Fi inactive.")
    print("It is a voltage estimate, not a battery charge percentage.")
    input("If the jumper is installed and Wi-Fi is off, press Enter. ")
    print("Estimated selected-rail voltage: {:.3f} V".format(
        _backend.read_battery_voltage()
    ))
    input("Compare with a meter if available, then press Enter to record. ")


def main():
    """Run direct checks against the maintained HardwareBackend class."""
    global _backend
    _backend = HardwareBackend()
    _backend.initialize()
    buttons = (
        ("A", "A"),
        ("B", "B"),
        ("up", "Up"),
        ("down", "Down"),
        ("left", "Left"),
        ("right", "Right"),
    )
    try:
        for button, label in buttons:
            _check("{} button".format(label), lambda b=button, n=label: _button(b, n))
        _check("Joystick", _joystick)
        _check("RGB indicator", _rgb_led)
        _check("Addressable LED strip", _led_strip)
        _check("Buzzer", lambda: _backend.play_tone(440, 500))
        _check("Display", _display)
        _check("Wi-Fi scan", _wifi)
        _check("GPIO HIGH/LOW loopback", _gpio_loopback)
        _check("GPIO PWM", _pwm)
        _check("ADC voltage", _adc)
        _check("Accelerometer", _accelerometer)
        _check("Battery / selected-rail voltage", _battery_voltage)
    finally:
        _backend.shutdown()

    print("\nHardware backend check summary:")
    for name, result in _results:
        print("{}: {}".format(result, name))


if __name__ == "__main__":
    main()
