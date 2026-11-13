"""Hardware backend backed by the archived eBadge MicroPython library.

The import of ``ebadge`` is delayed until ``initialize()`` so importing
``pybadge`` on a computer does not initialize hardware.
"""

from pybadge import UnsupportedFeatureError


class HardwareBackend:
    """Adapt the V4 MicroPython library to the shared ``pybadge`` API."""

    _BUTTON_NAMES = {
        "A": "button_a",
        "B": "button_b",
        "up": "button_up",
        "down": "button_down",
        "left": "button_left",
        "right": "button_right",
    }

    _COLOR_RGB = {
        "off": (0, 0, 0),
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "orange": (255, 128, 0),
        "magenta": (255, 0, 255),
        "cyan": (0, 255, 255),
        "purple": (128, 0, 128),
    }
    _ADC_PINS = (13, 14, 15, 16, 17, 18)
    _BATTERY_SENSE_PIN = 12
    _BATTERY_DIVIDER_GAIN = 16.0

    def __init__(self):
        self._ebadge = None
        self._machine = None
        self._pins = {}
        self._pin_modes = {}
        self._pwms = {}
        self._adcs = {}
        self._battery_adc = None

    def initialize(self):
        """Load the board library and initialize the display and outputs."""
        try:
            import ebadge
            import machine
        except ImportError:
            raise RuntimeError(
                "Hardware mode requires ebadge.py, board_v4.py, "
                "st7789py.py, and a VGA font on the badge filesystem."
            )

        self._ebadge = ebadge
        self._machine = machine
        ebadge.initialize()
        ebadge.turn_led_off()
        ebadge.clear_pixels()
        self.stop_tone()

    def shutdown(self):
        """Turn off outputs and release PWM resources configured by this API."""
        if self._ebadge is not None:
            self._ebadge.turn_led_off()
            self._ebadge.clear_pixels()
            self.stop_tone()

        for pwm in self._pwms.values():
            try:
                pwm.deinit()
            except AttributeError:
                pass
        self._pwms.clear()
        for adc in self._adcs.values():
            self._deinit_adc(adc)
        self._adcs.clear()
        if self._battery_adc is not None:
            self._deinit_adc(self._battery_adc)
            self._battery_adc = None
        self._pins.clear()
        self._pin_modes.clear()

    def is_pressed(self, button):
        name = self._BUTTON_NAMES[button]
        return self._ebadge.is_pressed(getattr(self._ebadge, name))

    def joystick(self):
        raise UnsupportedFeatureError(
            "Normalized joystick directions need V4.1.1 center and direction "
            "calibration before hardware support can be enabled."
        )

    def set_rgb_led(self, color):
        self._ebadge.set_led(self._rgb_value(color))

    def set_led_strip_pixel(self, index, color):
        self._ebadge.set_pixel(index, self._rgb_value(color))

    def set_led_strip(self, colors):
        board = self._ebadge._board
        board.addr_blank()
        for index, color in enumerate(colors):
            red, green, blue = self._rgb_value(color)
            board.addr_set(
                index,
                red // board.ADDR_LED_DIM,
                green // board.ADDR_LED_DIM,
                blue // board.ADDR_LED_DIM,
            )
        board.addr_show()

    def clear_led_strip(self):
        self._ebadge.clear_pixels()

    def play_tone(self, frequency_hz, duration_ms):
        """Play a blocking tone through the existing board helper."""
        self._ebadge.play_tone(frequency_hz, duration_ms)

    def stop_tone(self):
        if self._ebadge is None:
            return
        buzzer = self._ebadge._board.buzzer
        try:
            buzzer.duty(0)
        except AttributeError:
            buzzer.duty_u16(0)

    def display_clear(self, color):
        self._ebadge.display_clear(self._rgb565(color))

    def display_text(self, text, x, y, color):
        board = self._ebadge._board
        board.tft.text(
            board.font,
            str(text),
            int(x),
            int(y),
            self._rgb565(color),
            self._rgb565("black"),
        )

    def draw_pixel(self, x, y, color):
        self._ebadge.draw_pixel(x, y, self._rgb565(color))

    def draw_line(self, x1, y1, x2, y2, color):
        self._ebadge.draw_line(x1, y1, x2, y2, self._rgb565(color))

    def draw_rectangle(self, x, y, width, height, color, filled):
        self._ebadge.draw_rectangle(
            x, y, width, height, self._rgb565(color), filled=filled
        )

    def display_image(self, path, x, y):
        self._ebadge.display_image(path, x=x, y=y)

    def scan_wifi(self, include_details=False):
        """Scan visible access points using MicroPython's station interface."""
        try:
            import network
        except ImportError:
            raise RuntimeError("Wi-Fi scanning requires the network module")

        wlan = network.WLAN(network.STA_IF)
        was_active = wlan.active()
        if not was_active:
            wlan.active(True)
        try:
            raw_networks = wlan.scan()
        finally:
            if not was_active:
                wlan.active(False)

        results = []
        for record in raw_networks:
            ssid, _bssid, channel, rssi, authmode, _hidden = record
            if isinstance(ssid, bytes):
                ssid = ssid.decode()
            if include_details:
                results.append({
                    "ssid": ssid,
                    "signal_dbm": rssi,
                    "channel": channel,
                    "security": self._security_name(authmode),
                })
            else:
                results.append((ssid, rssi))
        return results

    def pause(self, milliseconds):
        self._ebadge.pause(milliseconds)

    def read_accelerometer(self):
        return self._ebadge.read_accelerometer()

    def read_battery_voltage(self):
        """Return an uncalibrated estimate of the jumper-selected rail."""
        self._require_wifi_inactive()
        if self._battery_adc is None:
            pin = self._machine.Pin(self._BATTERY_SENSE_PIN)
            self._battery_adc = self._new_adc(pin)
        divider_voltage = self._read_adc_voltage(self._battery_adc)
        return divider_voltage * self._BATTERY_DIVIDER_GAIN

    def configure_pin(self, pin, mode, pull):
        self.stop_pwm(pin)
        adc = self._adcs.pop(pin, None)
        if adc is not None:
            self._deinit_adc(adc)
        self._pins[pin] = self._ebadge.configure_pin(
            pin, mode=mode, pull=pull
        )
        self._pin_modes[pin] = mode

    def read_pin(self, pin):
        self._require_pin_mode(pin, "input")
        return self._ebadge.read_pin(pin)

    def write_pin(self, pin, value):
        self._require_pin_mode(pin, "output")
        self._ebadge.write_pin(pin, value)

    def read_voltage(self, pin):
        self._require_pin_mode(pin, "input")
        if pin not in self._ADC_PINS:
            raise ValueError("GPIO{} does not support ADC input".format(pin))
        self._require_wifi_inactive()
        adc = self._adcs.get(pin)
        if adc is None:
            adc = self._new_adc(self._pins[pin])
            self._adcs[pin] = adc
        return self._read_adc_voltage(adc)

    def set_pwm(self, pin, frequency_hz, duty_percent):
        self._require_pin_mode(pin, "output")
        pwm = self._pwms.get(pin)
        if pwm is None:
            pwm = self._machine.PWM(self._pins[pin])
            self._pwms[pin] = pwm
        pwm.freq(frequency_hz)
        duty_u16 = int(duty_percent * 65535 / 100)
        try:
            pwm.duty_u16(duty_u16)
        except AttributeError:
            pwm.duty(int(duty_percent * 1023 / 100))

    def stop_pwm(self, pin):
        pwm = self._pwms.pop(pin, None)
        if pwm is not None:
            pwm.deinit()

    def _require_pin_mode(self, pin, mode):
        if pin not in self._pins:
            raise ValueError("configure GPIO{} before using it".format(pin))
        if self._pin_modes[pin] != mode:
            raise ValueError(
                "configure GPIO{} as {} before using it".format(pin, mode)
            )

    def _require_wifi_inactive(self):
        try:
            import network
        except ImportError:
            return
        wlan = network.WLAN(network.STA_IF)
        if wlan.active():
            raise UnsupportedFeatureError(
                "GPIO13 through GPIO18 and GPIO12 use ADC2. Turn off Wi-Fi "
                "before taking an analog reading."
            )

    def _new_adc(self, pin):
        adc = self._machine.ADC(pin)
        try:
            adc.atten(self._machine.ADC.ATTN_11DB)
        except AttributeError:
            try:
                adc.init(atten=self._machine.ADC.ATTN_11DB)
            except AttributeError:
                self._deinit_adc(adc)
                raise UnsupportedFeatureError(
                    "The installed MicroPython firmware cannot configure "
                    "ADC attenuation."
                )
        return adc

    def _read_adc_voltage(self, adc):
        reader = getattr(adc, "read_uv", None)
        if reader is None:
            raise UnsupportedFeatureError(
                "Analog voltage requires a MicroPython firmware with "
                "machine.ADC.read_uv()."
            )
        return float(reader()) / 1000000.0

    @staticmethod
    def _deinit_adc(adc):
        deinit = getattr(adc, "deinit", None)
        if deinit is not None:
            deinit()

    @classmethod
    def _rgb_value(cls, color):
        if isinstance(color, str):
            return cls._COLOR_RGB[color]
        return tuple(color)

    @classmethod
    def _rgb565(cls, color):
        red, green, blue = cls._rgb_value(color)
        return ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)

    @staticmethod
    def _security_name(authmode):
        names = {
            0: "open",
            1: "WEP",
            2: "WPA-PSK",
            3: "WPA2-PSK",
            4: "WPA/WPA2-PSK",
            5: "WPA2-Enterprise",
            6: "WPA3-PSK",
        }
        return names.get(authmode, "unknown")
