"""Beginner-friendly interface for the BYU-Idaho eBadge.

Call :func:`initialize` before using a board helper. On a computer the default
mode is the interactive simulator; on MicroPython it is the physical board.
Tests can select the deterministic ``test`` mode.

Example::

    import pybadge

    pybadge.initialize()
    if pybadge.is_pressed(pybadge.BUTTON_A):
        pybadge.set_rgb_led("blue")
"""

BUTTON_A = "A"
BUTTON_B = "B"
BUTTON_UP = "up"
BUTTON_DOWN = "down"
BUTTON_LEFT = "left"
BUTTON_RIGHT = "right"

HIGH = 1
LOW = 0

GPIO13 = 13
GPIO14 = 14
GPIO15 = 15
GPIO16 = 16
GPIO17 = 17
GPIO18 = 18

OFF = "off"
BLACK = "black"
WHITE = "white"
RED = "red"
GREEN = "green"
BLUE = "blue"
YELLOW = "yellow"
ORANGE = "orange"
MAGENTA = "magenta"
CYAN = "cyan"
PURPLE = "purple"

_BUTTONS = (
    BUTTON_A,
    BUTTON_B,
    BUTTON_UP,
    BUTTON_DOWN,
    BUTTON_LEFT,
    BUTTON_RIGHT,
)
_COLOR_NAMES = (
    OFF,
    BLACK,
    WHITE,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    ORANGE,
    MAGENTA,
    CYAN,
    PURPLE,
)
_GPIO_PINS = (GPIO13, GPIO14, GPIO15, GPIO16, GPIO17, GPIO18)
_backend = None
_backend_mode = None


class NotInitializedError(RuntimeError):
    """Raised when a board helper is called before :func:`initialize`."""


class UnsupportedFeatureError(NotImplementedError):
    """Raised when the selected backend cannot represent a board feature."""


def initialize(mode="auto", backend=None):
    """Select and initialize the hardware, simulator, or test backend.

    ``auto`` selects physical hardware on MicroPython and the terminal
    simulator on a regular computer. Tests should use ``mode="test"``.
    An explicit ``backend`` object may be supplied with test mode.
    """
    global _backend, _backend_mode

    if mode not in ("auto", "hardware", "simulator", "test"):
        raise ValueError("mode must be 'auto', 'hardware', 'simulator', or 'test'")

    if _backend is not None:
        shutdown()

    selected_mode = mode
    if selected_mode == "auto":
        try:
            import machine  # noqa: F401
        except ImportError:
            selected_mode = "simulator"
        else:
            selected_mode = "hardware"

    if backend is not None:
        if selected_mode != "test":
            raise ValueError("a custom backend may only be supplied in test mode")
        selected_backend = backend
    elif selected_mode == "test":
        from backends.test_backend import TestBackend

        selected_backend = TestBackend()
    elif selected_mode == "hardware":
        from backends.hardware_backend import HardwareBackend

        selected_backend = HardwareBackend()
    else:
        from backends.simulator_backend import SimulatorBackend

        selected_backend = SimulatorBackend()

    selected_backend.initialize()
    _backend = selected_backend
    _backend_mode = selected_mode
    return selected_backend


def shutdown():
    """Stop the selected backend and release outputs it owns."""
    global _backend, _backend_mode

    if _backend is not None:
        _backend.shutdown()
    _backend = None
    _backend_mode = None


def current_mode():
    """Return the active mode name, or ``None`` before initialization."""
    return _backend_mode


def _require_backend():
    if _backend is None:
        raise NotInitializedError("call pybadge.initialize() before using board helpers")
    return _backend


def _validate_button(button):
    if button not in _BUTTONS:
        raise ValueError("button must be one of the BUTTON_* constants")


def _validate_color(color):
    if isinstance(color, str):
        name = color.lower()
        if name not in _COLOR_NAMES:
            raise ValueError("unknown color name: {}".format(color))
        return name
    if isinstance(color, (tuple, list)) and len(color) == 3:
        rgb = []
        for channel in color:
            if not isinstance(channel, int) or channel < 0 or channel > 255:
                raise ValueError("RGB channels must be integers from 0 to 255")
            rgb.append(channel)
        return tuple(rgb)
    raise TypeError("color must be a supported name or an (red, green, blue) tuple")


def _validate_pin(pin):
    if pin not in _GPIO_PINS:
        raise ValueError("pin must be GPIO13 through GPIO18")
    return pin


def is_pressed(button):
    """Return whether a named eBadge button is held down."""
    _validate_button(button)
    return bool(_require_backend().is_pressed(button))


def joystick():
    """Return ``(x, y)`` normalized to -1.0..1.0.

    Negative x means left and positive x right. Negative y means down and
    positive y up. Values near zero indicate that the stick is centered.
    """
    x_value, y_value = _require_backend().joystick()
    return _clamp_axis(x_value), _clamp_axis(y_value)


def _clamp_axis(value):
    value = float(value)
    if value < -1.0:
        return -1.0
    if value > 1.0:
        return 1.0
    return value


def set_rgb_led(color):
    """Set the small RGB indicator LED to a color name or RGB tuple."""
    _require_backend().set_rgb_led(_validate_color(color))


def turn_rgb_led_off():
    """Turn off the small RGB indicator LED."""
    _require_backend().set_rgb_led(OFF)


def set_led_strip_pixel(index, color):
    """Set one addressable strip LED by index, from 0 through 23."""
    if not isinstance(index, int) or index < 0 or index >= 24:
        raise ValueError("LED strip index must be from 0 to 23")
    _require_backend().set_led_strip_pixel(index, _validate_color(color))


def set_led_strip(colors):
    """Set all 24 addressable LEDs at once using a complete color frame."""
    if len(colors) != 24:
        raise ValueError("LED strip frame must contain exactly 24 colors")
    frame = [_validate_color(color) for color in colors]
    _require_backend().set_led_strip(frame)


def clear_led_strip():
    """Turn off all 24 addressable LEDs."""
    _require_backend().clear_led_strip()


def play_tone(frequency_hz, duration_ms):
    """Play a buzzer tone for the given frequency and duration."""
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be greater than zero")
    if duration_ms < 0:
        raise ValueError("duration_ms must not be negative")
    _require_backend().play_tone(int(frequency_hz), int(duration_ms))


def stop_tone():
    """Stop a buzzer tone immediately."""
    _require_backend().stop_tone()


def display_clear(color=BLACK):
    """Fill the simulated or physical display with a color."""
    _require_backend().display_clear(_validate_color(color))


def display_text(text, x=8, y=8, color=WHITE):
    """Draw text at display pixel coordinates using the given color."""
    _require_backend().display_text(str(text), int(x), int(y), _validate_color(color))


def display_image(path, x=0, y=0):
    """Display a prepared image resource at the given display coordinates."""
    if not isinstance(path, str):
        raise TypeError("path must be a string")
    _require_backend().display_image(path, int(x), int(y))


def scan_wifi(include_details=False):
    """List nearby Wi-Fi networks, optionally including advanced details."""
    if not isinstance(include_details, bool):
        raise TypeError("include_details must be True or False")
    return _require_backend().scan_wifi(include_details)


def pause(milliseconds):
    """Pause for the requested number of milliseconds."""
    if milliseconds < 0:
        raise ValueError("milliseconds must not be negative")
    _require_backend().pause(int(milliseconds))


def read_accelerometer():
    """Return ``(x, y, z)`` acceleration in g, or ``None`` if unavailable."""
    return _require_backend().read_accelerometer()


def read_battery_voltage():
    """Return battery voltage in volts (not a charge percentage)."""
    return _require_backend().read_battery_voltage()


def configure_pin(pin, mode="input", pull=None):
    """Configure an exposed GPIO as a digital input or output.

    GPIO13 through GPIO18 correspond to board header labels IO13 through IO18
    with the standard board bridge configuration. Only use 3.3 V logic.
    """
    _validate_pin(pin)
    if mode not in ("input", "output"):
        raise ValueError("mode must be 'input' or 'output'")
    if pull not in (None, "up", "down"):
        raise ValueError("pull must be None, 'up', or 'down'")
    _require_backend().configure_pin(pin, mode, pull)


def read_pin(pin):
    """Read a configured digital input and return ``HIGH`` or ``LOW``."""
    value = _require_backend().read_pin(_validate_pin(pin))
    return HIGH if value else LOW


def write_pin(pin, value):
    """Write ``HIGH`` or ``LOW`` to a configured digital output."""
    _require_backend().write_pin(_validate_pin(pin), _validate_level(value))


def _validate_level(value):
    if value not in (HIGH, LOW, True, False):
        raise ValueError("value must be HIGH, LOW, True, or False")
    return HIGH if value else LOW


def is_high(pin):
    """Return whether a configured digital input is ``HIGH``."""
    return read_pin(pin) == HIGH


def is_low(pin):
    """Return whether a configured digital input is ``LOW``."""
    return read_pin(pin) == LOW


def read_voltage(pin):
    """Return an analog input voltage in volts.

    The backend rejects pins without verified ADC support. Never apply voltage
    above the board's documented safe input range.
    """
    return float(_require_backend().read_voltage(_validate_pin(pin)))


def set_pwm(pin, frequency_hz=1000, duty_percent=50):
    """Set PWM on a configured output pin.

    Args:
        pin: A supported GPIO output pin.
        frequency_hz: Number of PWM cycles per second.
        duty_percent: Output-on portion of each cycle, from 0 to 100 percent.
            0 is always off; 100 is always on.
    """
    _validate_pin(pin)
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be greater than zero")
    if duty_percent < 0 or duty_percent > 100:
        raise ValueError("duty_percent must be from 0 to 100")
    _require_backend().set_pwm(pin, int(frequency_hz), float(duty_percent))


def stop_pwm(pin):
    """Stop PWM output on a configured GPIO."""
    _require_backend().stop_pwm(_validate_pin(pin))
