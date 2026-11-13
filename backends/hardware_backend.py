"""Direct MicroPython driver for the BYU-Idaho eBadge V4.1.1 hardware."""

from pybadge import UnsupportedFeatureError


class HardwareBackend:
    """Implement the public board operations using MicroPython peripherals."""

    _BUTTON_PINS = {
        "A": 34,
        "B": 33,
        "up": 11,
        "down": 47,
        "left": 21,
        "right": 10,
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
    _DISPLAY_WIDTH = 320
    _DISPLAY_HEIGHT = 240
    _DISPLAY_SPI_BAUDRATE = 60000000
    _RGB_PWM_PINS = (2, 4, 5)
    _RGB_PWM_MAX_DUTY = 30
    _BUZZER_PIN = 48
    _LED_STRIP_PIN = 7
    _LED_STRIP_COUNT = 24
    _LED_STRIP_DIM = 4
    _LED_STRIP_TIMING = (350, 800, 700, 600)
    _ACCELEROMETER_ADDRESS = 0x1C

    def __init__(self):
        self._machine = None
        self._utime = None
        self._display_driver = None
        self._font = None
        self._display = None
        self._buttons = {}
        self._rgb_pwms = []
        self._buzzer = None
        self._led_strip_pin = None
        self._led_strip = None
        self._pins = {}
        self._pin_modes = {}
        self._pwms = {}
        self._adcs = {}
        self._battery_adc = None
        self._accelerometer = None
        self._accelerometer_checked = False

    def initialize(self):
        """Set up the display, buttons, indicator, and buzzer."""
        try:
            import machine
            import utime
            from backends.hardware import st7789py, vga1_8x16
        except ImportError:
            raise RuntimeError(
                "Hardware mode requires MicroPython and the maintained "
                "backends/hardware display driver and font."
            )

        self._machine = machine
        self._utime = utime
        self._display_driver = st7789py
        self._font = vga1_8x16

        spi = machine.SPI(
            1,
            baudrate=self._DISPLAY_SPI_BAUDRATE,
            polarity=1,
            phase=0,
            sck=machine.Pin(46),
            mosi=machine.Pin(3),
            miso=machine.Pin(12),
        )
        self._display = st7789py.ST7789(
            spi,
            240,
            320,
            reset=machine.Pin(1, machine.Pin.OUT),
            cs=machine.Pin(0, machine.Pin.OUT),
            dc=machine.Pin(45, machine.Pin.OUT),
            rotation=3,
            color_order=st7789py.BGR,
        )
        self._display.init([])
        self._display.fill(self._rgb565("black"))

        self._buttons = {
            name: machine.Pin(number, machine.Pin.IN)
            for name, number in self._BUTTON_PINS.items()
        }
        self._rgb_pwms = [
            machine.PWM(machine.Pin(number), freq=1000)
            for number in self._RGB_PWM_PINS
        ]
        self._buzzer = machine.PWM(machine.Pin(self._BUZZER_PIN), freq=1000)
        self._led_strip_pin = machine.Pin(
            self._LED_STRIP_PIN, machine.Pin.OUT, value=0
        )
        self.turn_rgb_led_off()
        self.stop_tone()
        try:
            self.clear_led_strip()
        except UnsupportedFeatureError:
            # The remaining hardware features can still work without this module.
            pass

    def shutdown(self):
        """Turn off owned outputs and release ADC and PWM resources."""
        self.turn_rgb_led_off()
        self.clear_led_strip()
        self.stop_tone()

        for pwm in self._pwms.values():
            self._deinit(pwm)
        self._pwms.clear()
        for pwm in self._rgb_pwms:
            self._deinit(pwm)
        self._rgb_pwms = []
        if self._buzzer is not None:
            self._deinit(self._buzzer)
            self._buzzer = None

        for adc in self._adcs.values():
            self._deinit(adc)
        self._adcs.clear()
        if self._battery_adc is not None:
            self._deinit(self._battery_adc)
            self._battery_adc = None
        if self._accelerometer is not None:
            self._deinit(self._accelerometer)
            self._accelerometer = None
        self._pins.clear()
        self._pin_modes.clear()
        self._buttons.clear()
        self._display = None
        self._led_strip = None

    def is_pressed(self, button):
        """Return whether a named physical button is held down."""
        return bool(self._buttons[button].value())

    def joystick(self):
        """Raise until physical center and direction calibration is complete."""
        raise UnsupportedFeatureError(
            "Normalized joystick directions need V4.1.1 center and direction "
            "calibration before hardware support can be enabled."
        )

    def set_rgb_led(self, color):
        """Set the small onboard RGB indicator."""
        red, green, blue = self._rgb_value(color)
        channels = (red, green, blue)
        for pwm, value in zip(self._rgb_pwms, channels):
            duty = int(value / 255 * self._RGB_PWM_MAX_DUTY / 255 * 1023)
            self._set_pwm_duty(pwm, duty, 1023)

    def turn_rgb_led_off(self):
        """Turn off the small onboard RGB indicator."""
        for pwm in self._rgb_pwms:
            self._set_pwm_duty(pwm, 0, 1023)

    def set_led_strip_pixel(self, index, color):
        """Set one of the 24 addressable LEDs and refresh the strip."""
        strip = self._ensure_led_strip()
        red, green, blue = self._rgb_value(color)
        strip[index] = (
            red // self._LED_STRIP_DIM,
            green // self._LED_STRIP_DIM,
            blue // self._LED_STRIP_DIM,
        )
        strip.write()

    def set_led_strip(self, colors):
        """Update all addressable LEDs as one frame."""
        strip = self._ensure_led_strip()
        strip.fill((0, 0, 0))
        for index, color in enumerate(colors):
            red, green, blue = self._rgb_value(color)
            strip[index] = (
                red // self._LED_STRIP_DIM,
                green // self._LED_STRIP_DIM,
                blue // self._LED_STRIP_DIM,
            )
        strip.write()

    def clear_led_strip(self):
        """Turn off all addressable LEDs."""
        if self._led_strip is not None:
            self._led_strip.fill((0, 0, 0))
            self._led_strip.write()

    def play_tone(self, frequency_hz, duration_ms):
        """Play a buzzer tone for the requested duration."""
        self._buzzer.freq(frequency_hz)
        self._set_pwm_duty(self._buzzer, 512, 1023)
        self._utime.sleep_ms(duration_ms)
        self.stop_tone()

    def stop_tone(self):
        """Stop the buzzer immediately."""
        if self._buzzer is not None:
            self._set_pwm_duty(self._buzzer, 0, 1023)

    def display_clear(self, color):
        """Fill the display with a color."""
        self._display.fill(self._rgb565(color))

    def display_text(self, text, x, y, color):
        """Draw text with a black background at display coordinates."""
        self._display.text(
            self._font,
            str(text),
            x,
            y,
            self._rgb565(color),
            self._rgb565("black"),
        )

    def draw_pixel(self, x, y, color):
        """Draw one display pixel."""
        self._display.pixel(x, y, self._rgb565(color))

    def draw_line(self, x1, y1, x2, y2, color):
        """Draw a display line."""
        self._display.line(x1, y1, x2, y2, self._rgb565(color))

    def draw_rectangle(self, x, y, width, height, color, filled):
        """Draw an outlined or filled display rectangle."""
        draw = self._display.fill_rect if filled else self._display.rect
        draw(x, y, width, height, self._rgb565(color))

    def display_image(self, path, x, y):
        """Draw an uncompressed 24-bit BMP, shrinking it to fit the display."""
        with open(path, "rb") as image_file:
            header = image_file.read(54)
            if len(header) < 54 or header[:2] != b"BM":
                raise ValueError("image must be a BMP file")
            pixel_offset = int.from_bytes(header[10:14], "little")
            width = int.from_bytes(header[18:22], "little", signed=True)
            signed_height = int.from_bytes(header[22:26], "little", signed=True)
            bits = int.from_bytes(header[28:30], "little")
            compression = int.from_bytes(header[30:34], "little")
            if width <= 0 or signed_height == 0 or bits != 24 or compression != 0:
                raise ValueError("only uncompressed 24-bit BMP images are supported")

            height = abs(signed_height)
            top_down = signed_height < 0
            scale = min(
                1.0,
                self._DISPLAY_WIDTH / width,
                self._DISPLAY_HEIGHT / height,
            )
            output_width = max(1, int(width * scale))
            output_height = max(1, int(height * scale))
            row_bytes = ((width * 3 + 3) // 4) * 4

            for output_y in range(output_height):
                source_y = int(output_y / scale)
                bitmap_y = source_y if top_down else height - 1 - source_y
                image_file.seek(pixel_offset + bitmap_y * row_bytes)
                row = image_file.read(row_bytes)
                if len(row) < row_bytes:
                    raise ValueError("BMP image ended before all pixel rows were read")
                pixels = bytearray(output_width * 2)
                for output_x in range(output_width):
                    source_x = int(output_x / scale)
                    offset = source_x * 3
                    blue, green, red = row[offset], row[offset + 1], row[offset + 2]
                    color = self._rgb565((red, green, blue))
                    byte_index = output_x * 2
                    if self._display.needs_swap:
                        pixels[byte_index] = color & 0xFF
                        pixels[byte_index + 1] = color >> 8
                    else:
                        pixels[byte_index] = color >> 8
                        pixels[byte_index + 1] = color & 0xFF
                self._display.blit_buffer(
                    pixels, x, y + output_y, output_width, 1
                )

    def scan_wifi(self, include_details=False):
        """Scan visible Wi-Fi networks, restoring the prior radio state."""
        try:
            import network
        except ImportError:
            raise RuntimeError("Wi-Fi scanning requires the network module")

        wlan = network.WLAN(network.STA_IF)
        was_active = wlan.active()
        if not was_active:
            wlan.active(True)
        try:
            records = wlan.scan()
        finally:
            if not was_active:
                wlan.active(False)

        results = []
        for record in records:
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
        """Pause for the requested number of milliseconds."""
        self._utime.sleep_ms(milliseconds)

    def read_accelerometer(self):
        """Return acceleration in g, or ``None`` if the sensor is unavailable."""
        if not self._accelerometer_checked:
            self._accelerometer_checked = True
            try:
                self._accelerometer = self._machine.I2C(
                    0,
                    scl=self._machine.Pin(42),
                    sda=self._machine.Pin(41),
                    freq=400000,
                )
                if (
                    self._ACCELEROMETER_ADDRESS not in self._accelerometer.scan()
                    or self._accelerometer.readfrom_mem(
                        self._ACCELEROMETER_ADDRESS, 0x0D, 1
                    )[0] not in (0x1A, 0x2A)
                ):
                    self._accelerometer = None
                    return None
                self._accelerometer.writeto_mem(
                    self._ACCELEROMETER_ADDRESS, 0x0E, b"\x00"
                )
                self._accelerometer.writeto_mem(
                    self._ACCELEROMETER_ADDRESS, 0x2A, b"\x01"
                )
            except OSError:
                self._accelerometer = None
                return None

        if self._accelerometer is None:
            return None
        try:
            data = self._accelerometer.readfrom_mem(
                self._ACCELEROMETER_ADDRESS, 0x01, 6
            )
        except OSError:
            return None

        values = []
        for index in (0, 2, 4):
            raw = ((data[index] << 8) | data[index + 1]) >> 2
            if raw > 8191:
                raw -= 16384
            values.append(raw / 1024.0)
        return tuple(values)

    def read_battery_voltage(self):
        """Return an uncalibrated estimate of the jumper-selected rail."""
        self._require_wifi_inactive()
        if self._battery_adc is None:
            pin = self._machine.Pin(self._BATTERY_SENSE_PIN)
            self._battery_adc = self._new_adc(pin)
        return self._read_adc_voltage(self._battery_adc) * self._BATTERY_DIVIDER_GAIN

    def configure_pin(self, pin, mode, pull):
        """Configure one exposed GPIO and release conflicting resources."""
        self.stop_pwm(pin)
        adc = self._adcs.pop(pin, None)
        if adc is not None:
            self._deinit(adc)

        pin_mode = self._machine.Pin.IN if mode == "input" else self._machine.Pin.OUT
        if pull is None:
            configured_pin = self._machine.Pin(pin, pin_mode)
        else:
            pull_mode = (
                self._machine.Pin.PULL_UP
                if pull == "up"
                else self._machine.Pin.PULL_DOWN
            )
            configured_pin = self._machine.Pin(pin, pin_mode, pull=pull_mode)
        self._pins[pin] = configured_pin
        self._pin_modes[pin] = mode

    def read_pin(self, pin):
        """Read a previously configured digital input."""
        self._require_pin_mode(pin, "input")
        return self._pins[pin].value()

    def write_pin(self, pin, value):
        """Write a logic level to a previously configured digital output."""
        self._require_pin_mode(pin, "output")
        self._pins[pin].value(value)

    def read_voltage(self, pin):
        """Read an ADC2 input voltage while Wi-Fi is inactive."""
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
        """Set PWM on a previously configured output GPIO."""
        self._require_pin_mode(pin, "output")
        pwm = self._pwms.get(pin)
        if pwm is None:
            pwm = self._machine.PWM(self._pins[pin])
            self._pwms[pin] = pwm
        pwm.freq(frequency_hz)
        duty = int(duty_percent * 65535 / 100)
        self._set_pwm_duty(pwm, duty, 65535)

    def stop_pwm(self, pin):
        """Stop and release PWM configured on a GPIO."""
        pwm = self._pwms.pop(pin, None)
        if pwm is not None:
            self._deinit(pwm)

    def _ensure_led_strip(self):
        if self._led_strip is not None:
            return self._led_strip
        try:
            import neopixel
        except ImportError:
            raise UnsupportedFeatureError(
                "The MicroPython neopixel module is required for the LED strip."
            )
        self._led_strip = neopixel.NeoPixel(
            self._led_strip_pin,
            self._LED_STRIP_COUNT,
            timing=self._LED_STRIP_TIMING,
        )
        return self._led_strip

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
                "GPIO12 through GPIO18 use ADC2. Turn off Wi-Fi before "
                "taking an analog reading."
            )

    def _new_adc(self, pin):
        adc = self._machine.ADC(pin)
        try:
            adc.atten(self._machine.ADC.ATTN_11DB)
        except AttributeError:
            try:
                adc.init(atten=self._machine.ADC.ATTN_11DB)
            except AttributeError:
                self._deinit(adc)
                raise UnsupportedFeatureError(
                    "The installed MicroPython firmware cannot configure "
                    "ADC attenuation."
                )
        return adc

    def _read_adc_voltage(self, adc):
        reader = getattr(adc, "read_uv", None)
        if reader is None:
            raise UnsupportedFeatureError(
                "Analog voltage requires MicroPython machine.ADC.read_uv()."
            )
        return float(reader()) / 1000000.0

    def _set_pwm_duty(self, pwm, duty, maximum):
        if hasattr(pwm, "duty_u16"):
            duty_u16 = int(duty * 65535 / maximum)
            pwm.duty_u16(duty_u16)
        else:
            pwm.duty(int(duty * 1023 / maximum))

    @staticmethod
    def _deinit(resource):
        deinit = getattr(resource, "deinit", None)
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
