"""Deterministic backend used by pytest and headless examples."""


class TestBackend:
    """In-memory eBadge model with controllable inputs and inspectable output."""

    def __init__(self):
        self.buttons = {}
        self.joystick_values = (0.0, 0.0)
        self.rgb_led = "off"
        self.led_strip = ["off"] * 24
        self.tones = []
        self.active_tone = None
        self.display_color = "black"
        self.display_operations = []
        self.wifi_results = []
        self.digital_inputs = {}
        self.analog_inputs = {}
        self.pin_modes = {}
        self.pwm_outputs = {}
        self.accelerometer_values = (0.0, 0.0, 1.0)
        self.battery_voltage = 4.0
        self.initialized = False

    def initialize(self):
        self.initialized = True

    def shutdown(self):
        self.initialized = False
        self.rgb_led = "off"
        self.led_strip = ["off"] * 24
        self.active_tone = None
        self.pwm_outputs.clear()

    def is_pressed(self, button):
        return bool(self.buttons.get(button, False))

    def joystick(self):
        return self.joystick_values

    def set_rgb_led(self, color):
        self.rgb_led = color

    def set_led_strip_pixel(self, index, color):
        self.led_strip[index] = color

    def set_led_strip(self, colors):
        self.led_strip = list(colors)

    def clear_led_strip(self):
        self.led_strip = ["off"] * 24

    def play_tone(self, frequency_hz, duration_ms):
        request = (frequency_hz, duration_ms)
        self.tones.append(request)
        self.active_tone = request

    def stop_tone(self):
        self.active_tone = None

    def display_clear(self, color):
        self.display_color = color
        self.display_operations.append(("clear", color))

    def display_text(self, text, x, y, color):
        operation = ("text", text, x, y, color)
        self.display_operations.append(operation)

    def draw_pixel(self, x, y, color):
        self.display_operations.append(("pixel", x, y, color))

    def draw_line(self, x1, y1, x2, y2, color):
        self.display_operations.append(("line", x1, y1, x2, y2, color))

    def draw_rectangle(self, x, y, width, height, color, filled):
        self.display_operations.append(
            ("rectangle", x, y, width, height, color, filled)
        )

    def display_image(self, path, x, y):
        self.display_operations.append(("image", path, x, y))

    def scan_wifi(self, include_details=False):
        if include_details:
            return [dict(network) for network in self.wifi_results]
        return [
            (network.get("ssid", ""), network.get("signal_dbm", -100))
            for network in self.wifi_results
        ]

    def pause(self, milliseconds):
        return None

    def read_accelerometer(self):
        return self.accelerometer_values

    def read_battery_voltage(self):
        return self.battery_voltage

    def configure_pin(self, pin, mode, pull):
        self.pin_modes[pin] = (mode, pull)
        if mode == "input":
            self.digital_inputs.setdefault(pin, 0)
            self.analog_inputs.setdefault(pin, 0.0)

    def read_pin(self, pin):
        mode, _pull = self.pin_modes.get(pin, (None, None))
        if mode != "input":
            raise ValueError("configure the pin as an input before reading it")
        return 1 if self.digital_inputs.get(pin, 0) else 0

    def write_pin(self, pin, value):
        mode, _pull = self.pin_modes.get(pin, (None, None))
        if mode != "output":
            raise ValueError("configure the pin as an output before writing it")
        self.digital_inputs[pin] = value

    def read_voltage(self, pin):
        mode, _pull = self.pin_modes.get(pin, (None, None))
        if mode != "input":
            raise ValueError("configure the pin as an input before reading voltage")
        if pin not in self.analog_inputs:
            raise ValueError("GPIO{} does not have ADC support".format(pin))
        return float(self.analog_inputs[pin])

    def set_pwm(self, pin, frequency_hz, duty_percent):
        mode, _pull = self.pin_modes.get(pin, (None, None))
        if mode != "output":
            raise ValueError("configure the pin as an output before setting PWM")
        self.pwm_outputs[pin] = (frequency_hz, duty_percent)

    def stop_pwm(self, pin):
        self.pwm_outputs.pop(pin, None)

    def press_button(self, button):
        """Set a simulated button input to pressed."""
        self.buttons[button] = True

    def release_button(self, button):
        """Set a simulated button input to released."""
        self.buttons[button] = False

    def set_joystick(self, x, y):
        """Set the simulated normalized joystick position."""
        self.joystick_values = (float(x), float(y))

    def set_pin_level(self, pin, value):
        """Set a digital input level for a configured input pin."""
        self.digital_inputs[pin] = 1 if value else 0

    def set_pin_voltage(self, pin, volts):
        """Set an analog input voltage for a configured input pin."""
        if volts < 0 or volts > 3.3:
            raise ValueError("test voltage must be from 0.0 to 3.3 volts")
        self.analog_inputs[pin] = float(volts)

    def set_wifi_results(self, networks):
        """Set Wi-Fi scan results for a test."""
        self.wifi_results = [dict(network) for network in networks]

    def set_accelerometer(self, x, y, z):
        """Set accelerometer values, in g, for a test."""
        self.accelerometer_values = (float(x), float(y), float(z))

    def set_battery_voltage(self, volts):
        """Set the test battery voltage in volts."""
        self.battery_voltage = float(volts)
