# Draft `pybadge.py` public API for review

**Status: user-reviewed; implementation in progress.** Agreed decisions are
recorded below. Advanced Wi-Fi result fields and exact test-helper names still
need implementation-level choices.

## Runtime selection

Proposed startup:

```python
import pybadge

pybadge.initialize()                  # hardware on the badge; simulator on a computer
pybadge.initialize(mode="test")       # deterministic, headless test backend
```

**Agreed:** mode names are `"hardware"`, `"simulator"`, and `"test"`, with
`"auto"` as the default. Auto selects hardware on an eBadge and the interactive
simulator on a computer; tests explicitly select `mode="test"`. Importing
`pybadge` alone should not initialize a radio, draw a terminal interface, or
touch hardware. `shutdown()` should put owned outputs and services into a safe
inactive state. The simulator is a focused approximation for buttons, screen,
LEDs, and buzzer, not a complete electrical or wireless model. Its blue board
artwork permanently displays the BYU-Idaho logo; program output appears in the
separate simulated screen area.

## Candidate user functions

| Function | Proposed behavior |
| --- | --- |
| `is_pressed(button)` | Return `True` while one of the named board buttons is held. **Agreed:** accept constants such as `BUTTON_A`, `BUTTON_B`, `BUTTON_UP`, `BUTTON_DOWN`, `BUTTON_LEFT`, and `BUTTON_RIGHT`. |
| `joystick()` | **Agreed:** return an `(x, y)` tuple normalized from `-1.0` to `1.0`. `x=-1` means left, `x=1` right; `y=-1` means down, `y=1` up; values near zero mean centered. |
| `set_rgb_led(color)` / `turn_rgb_led_off()` | **Agreed names.** Set or turn off the small onboard RGB LED. Accept simple color names or an `(red, green, blue)` tuple with channels from 0 to 255. |
| `set_led_strip_pixel(index, color)` / `clear_led_strip()` | **Agreed names.** Set one of the 24 addressable LEDs or turn the full strip off. Accept the agreed color names or RGB tuples. |
| `set_led_strip(colors)` | **Agreed name.** Set all 24 addressable LEDs from one list of colors and update the strip as one frame. Accept the agreed color names or RGB tuples. Animation timing stays in the calling program's loop via `pause(milliseconds)`. |
| `play_tone(frequency_hz, duration_ms)` / `stop_tone()` | Play a buzzer tone for the requested duration, or stop it early. |
| `display_clear(color=BLACK)` | Fill the LCD with a color. |
| `display_text(text, x=8, y=8, color=WHITE)` | Draw text at pixel coordinates. |
| `draw_pixel(x, y, color=WHITE)` / `draw_line(x1, y1, x2, y2, color=WHITE)` | Draw a pixel or line on the display. |
| `draw_rectangle(x, y, width, height, color=WHITE, filled=False)` | Draw an outline or filled rectangle. |
| `display_image(path, x=0, y=0)` | Display an image resource in the format supported by the active backend. For hardware, use a prepared display asset generated from a PNG/JPG source. |
| `scan_wifi(include_details=False)` | **Agreed:** by default, return nearby networks as `(ssid, signal_dbm)` pairs. When `include_details=True`, return richer network records. Candidate extra fields are channel and security/authentication; exact record shape remains open. |
| `pause(milliseconds)` | Pause for the requested number of milliseconds. |
| `read_accelerometer()` | **Agreed for first API:** return `(x, y, z)` acceleration readings in g, or `None` if the sensor cannot be read. |
| `read_battery_voltage()` | **Agreed for first API:** return battery voltage in volts, not an estimated charge percentage. |

## External GPIO functions (added for review)

The archived `ebadge.py` accepts GPIO numbers 13 through 18 for external
connections. The V4.1.1 production netlist confirms these signals are routed
to J9 contacts 1, 3, 5, 7, 9, and 11. The board silk labels them `IO13` through
`IO18`; software should name them by ESP32 GPIO number. All built-in peripheral
helpers assume the board's standard jumper-bridge positions. The API must not
assume it can detect when a user changes those physical bridges. The first
version supports only the standard routing for built-in helpers. For a changed
route, users can address the actual GPIO through the external pin helpers;
remapping built-in helpers is not part of the current API.

Proposed constants and functions:

```python
HIGH = 1
LOW = 0
GPIO13 = 13
GPIO14 = 14
# ...through GPIO18

pybadge.configure_pin(pybadge.GPIO13, mode="input")
pybadge.configure_pin(pybadge.GPIO14, mode="output")
pybadge.write_pin(pybadge.GPIO14, HIGH)
level = pybadge.read_pin(pybadge.GPIO13)  # digital input: HIGH or LOW
if pybadge.is_high(pybadge.GPIO13):
    ...
if pybadge.is_low(pybadge.GPIO13):
    ...
volts = pybadge.read_voltage(pybadge.GPIO13)  # voltage, in volts
pybadge.set_pwm(pybadge.GPIO14, frequency_hz=1000, duty_percent=50)
pybadge.stop_pwm(pybadge.GPIO14)
```

Proposed PWM docstring wording:

```python
def set_pwm(pin, frequency_hz=1000, duty_percent=50):
    """Set PWM on a configured output pin.

    Args:
        pin: A supported GPIO output pin.
        frequency_hz: Number of PWM cycles per second.
        duty_percent: Output-on portion of each cycle, from 0 to 100 percent.
            0 is always off; 100 is always on.
    """
```

An analog-to-digital converter (ADC) lets a pin measure a changing voltage as a
number. A digital GPIO read only says whether the signal is LOW or HIGH; it
does not report intermediate voltage levels. **Agreed:** `read_voltage()`
returns volts and rejects pins that are not verified as ADC-capable with a
clear error. `read_pin()`, `is_high()`, and `is_low()` are digital reads and
remain available on verified digital-input GPIOs whether or not they support
ADC. GPIO13–GPIO18 are ADC2 inputs on the ESP32-S3 and are routed to the V4.1.1
expansion header. Document the ADC's measurement range and its Wi-Fi restriction.
GPIO uses 3.3 V logic; the software cannot protect a pin from an over-voltage
connection. PWM should be limited to verified output pins and use an
approachable duty percentage from 0 to 100. Physical readings still need
validation on the badge.

**Deferred future work:** Bluetooth Low Energy (BLE) and SD-card support are
not part of the first API. Add them in a later iteration after firmware
availability and board wiring are verified.

## Test access

The test mode needs deterministic inputs and observable outputs. One option is
to expose a test backend/factory through a separate testing module, for example:

```python
from pybadge.testing import make_backend

backend = make_backend()
pybadge.initialize(mode="test", backend=backend)
backend.press_button(pybadge.BUTTON_A)
assert pybadge.is_pressed(pybadge.BUTTON_A)
```

**Agreed:** support both a pytest fixture and a context manager if they can
share the same small setup/cleanup API without duplicating complexity. Tests
should also be able to set digital and analog input values and inspect
LED colors, addressable LED colors, requested PWM settings and tones, display
calls, and Wi-Fi scan results without a TUI or physical board. The exact test
helper names are open for review.

## Decisions to review

1. **Agreed:** `initialize()` selects hardware automatically on the badge and
   the interactive simulator on a computer; tests explicitly select
   `mode="test"`.
2. **Agreed:** use named button constants (`BUTTON_A`, `BUTTON_UP`, etc.).
3. **Agreed:** `joystick()` returns an `(x, y)` tuple normalized from `-1.0`
   to `1.0`. Negative `x` means left and positive `x` right; negative `y`
   means down and positive `y` up; values near `(0, 0)` mean centered.
4. **Agreed:** accept both color names and RGB tuples with channel values
   from 0 to 255. Use `set_rgb_led()` for the small RGB LED,
   `set_led_strip_pixel()` / `set_led_strip()` for the addressable strip, and
   `clear_led_strip()` to turn off the strip.
5. **Agreed:** `scan_wifi(include_details=False)` returns `(ssid, signal_dbm)`
   pairs by default; `include_details=True` asks for advanced network
   information. The extra fields and detailed result structure remain to be
   decided.
6. **Agreed:** support both a pytest fixture and a context manager, as long as
   they share a simple implementation and do not add much complexity.
7. **Agreed direction:** keep PNG/JPG source images and provide a host-side
   `resize_image.py` utility that resizes an image for the 320 × 240 display
   and writes a 24-bit BMP for the hardware backend. The logo example will
   display the converted BMP. Confirm exact sizing options and output naming
   when implementing the utility.
8. **Agreed:** provide external pin setup/read/write helpers and convenient
   `is_high` and `is_low` checks, subject to V4.1.1 pin verification.
9. **Clarified:** use GPIO13 through GPIO18, which correspond to board labels
   IO13 through IO18 on the default header wiring. The public API should expose
   named constants such as `GPIO13` to make the GPIO-number meaning explicit.
   Espressif identifies these as ADC2 channels 2 through 7 on the ESP32-S3;
   ADC reads need validation against the board's target firmware.
10. **Agreed:** `read_voltage(pin)` returns volts and rejects pins that are
    not verified ADC inputs. Digital `read_pin()`/`is_high()`/`is_low()` remain
    available on verified digital inputs without ADC.
11. **Agreed:** `set_pwm(pin, frequency_hz, duty_percent)` uses a duty
    percentage from 0 to 100. Document the units in the README and function
    docstring; 0 means always off and 100 always on.
12. **Agreed:** `set_led_strip_pixel()` updates one LED,
    `set_led_strip(colors)` sends a complete frame, and the program's loop
    calls `pause(milliseconds)` between frames. No separate buffer/flush
    operation or animation helper is needed in the first version.
13. **Agreed:** include accelerometer readings and battery voltage in the first
    API. Defer BLE and SD-card support to future work.

Please revise this proposal before the implementation task begins. The API
should favor clear, predictable behavior for users over one-to-one exposure
of low-level driver calls.
