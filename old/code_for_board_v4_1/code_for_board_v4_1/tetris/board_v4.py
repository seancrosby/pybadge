"""
board_v4 — ESP32-S3 e-Badge v4.0 (MicroPython).

This module is shared "plumbing" for the lesson .py files: it connects Python to your
badge hardware (screen, buttons, joystick, buzzer, RGB LED, and the pixel ring).
After tft_init(), print(...) in your lesson shows on the TFT (not in Thonny's shell
unless you use builtins.print).

Needs on the device: st7789py.py and a VGA font (vga1_8x16.py preferred, else vga1_8x8.py).

Lessons: use print(...) like normal Python — text goes to the TFT console (not USB).
For serial debug on a PC, use builtins.print("...").

  from board_v4 import *
  tft_init()                            # default: full-height console, no status strip
  tft_init(include_status_bar=True)     # show bottom button/joystick status strip
  print("Hello", "world", 42)           # sep=" " like Python
  print("ok", fg=st7789.CYAN)           # optional color (board extension)
  set_rgb_color(RED)                     # or "red", or set_rgb_color(255, 0, 0)
  println_reset()                       # clear console; status strip updates
  tft_clear()                           # whole screen + status strip
  sleep(1000)                           # wait 1 second (milliseconds)
  addr_blank()                          # clear strip RAM; px(...); addr_show() once per frame
"""

import builtins
import machine
import st7789py as st7789
try:
    import vga1_8x16 as font
except ImportError:
    import vga1_8x8 as font
import utime


def sleep(ms):
    """Pause for ``ms`` milliseconds — same as ``utime.sleep_ms(ms)``, shorter for lessons."""
    utime.sleep_ms(ms)


# Default text color for print() when you omit fg= ...
DEFAULT_TEXT_COLOR = st7789.WHITE

# --- Pin numbers on this PCB (not the objects you read in lessons; see button_* below) ---
TFT_SCLK = 46
TFT_MOSI = 3
TFT_MISO = 12
TFT_RST = 1
TFT_CS = 0
TFT_DC = 45

PIN_UP = 11
PIN_DOWN = 47
PIN_LEFT = 21
PIN_RIGHT = 10
PIN_B = 33
PIN_A = 34

PIN_RED = 2
PIN_GREEN = 4
PIN_BLUE = 5
PIN_BUZZER = 48
PIN_ADDR_LEDS = 7
PHYS_ADDR_LEDS = 24
NUM_ADDR_LEDS = PHYS_ADDR_LEDS

# Addressable strip: soft brightness so the ring is comfortable to look at (divide RGB here).
ADDR_LED_DIM = 4
# Explicit WS2812 timing is more stable on the ESP32-S3 MicroPython build than
# the NeoPixel driver's default timing for this board.
ADDR_LED_TIMING = (350, 800, 700, 600)

# Names for px(index, color) — use like px(0, RED) or px(1, "green").
OFF = "off"
RED = "red"
GREEN = "green"
BLUE = "blue"
YELLOW = "yellow"
ORANGE = "orange"
MAGENTA = "magenta"
CYAN = "cyan"
WHITE = "white"
PURPLE = "purple"
SLATE = "slate"

_LED_PALETTE = {
    OFF: (0, 0, 0),
    RED: (255, 0, 0),
    GREEN: (0, 255, 0),
    BLUE: (0, 0, 255),
    YELLOW: (255, 255, 0),
    ORANGE: (255, 128, 0),
    MAGENTA: (255, 0, 255),
    CYAN: (0, 255, 255),
    WHITE: (255, 255, 255),
    PURPLE: (80, 0, 80),
    SLATE: (64, 64, 255),
}

PWM_MAX_DUTY = 30

DISPLAY_W = 320
DISPLAY_H = 240

MARGIN_X = 8
MARGIN_Y = 6
CONSOLE_PAD = 6

# Filled in by _layout_recalc() after font import and when status bar on/off changes.
LINE_PX = 20
STATUS_BAR_H = 44
STATUS_BAR_TOP = DISPLAY_H
PRINT_LAST_START_Y = DISPLAY_H - 24
MAX_LINE_CHARS = 36

STATUS_SEP_COLOR = 0x632C
STATUS_BG_COLOR = 0x1082

_status_bar_enabled = True


def _layout_recalc():
    global LINE_PX, STATUS_BAR_H, STATUS_BAR_TOP, PRINT_LAST_START_Y, MAX_LINE_CHARS
    fh = getattr(font, "HEIGHT", 8)
    fw = getattr(font, "WIDTH", 8)
    LINE_PX = fh + 4
    MAX_LINE_CHARS = max(10, (DISPLAY_W - 2 * MARGIN_X) // fw)
    if _status_bar_enabled:
        STATUS_BAR_H = max(44, 2 * LINE_PX + 12)
        STATUS_BAR_TOP = DISPLAY_H - STATUS_BAR_H
        PRINT_LAST_START_Y = STATUS_BAR_TOP - CONSOLE_PAD - LINE_PX
    else:
        STATUS_BAR_H = 0
        STATUS_BAR_TOP = DISPLAY_H
        PRINT_LAST_START_Y = DISPLAY_H - LINE_PX - CONSOLE_PAD


def set_status_bar_enabled(on):
    """False = full-height console (e.g. boot menu). True = bottom input strip for lessons."""
    global _status_bar_enabled, _status_last
    _status_bar_enabled = bool(on)
    _status_last = None
    _layout_recalc()


def draw_console_line_at_row(row, text, fg):
    """One console line by row index (0 = top). For boot menu without full println_reset."""
    y = MARGIN_Y + int(row) * LINE_PX
    tft.fill_rect(0, y, DISPLAY_W, LINE_PX, st7789.BLACK)
    tft.text(font, _clip(str(text)), MARGIN_X, y, fg, st7789.BLACK)


_layout_recalc()
_jx = None
_jy = None
_addr_np = None  # lazy init NeoPixel instance
_addr_pin = machine.Pin(PIN_ADDR_LEDS, machine.Pin.OUT, value=0)
# Last status strip text; None means next paint does full bar background + both lines.
_status_last = None

# --- SPI + display (same init as tetris-micropython v4) ---
spi = machine.SPI(
    1,
    baudrate=60000000,
    polarity=1,
    phase=0,
    sck=machine.Pin(TFT_SCLK),
    mosi=machine.Pin(TFT_MOSI),
    miso=machine.Pin(TFT_MISO),
)

tft = st7789.ST7789(
    spi,
    240,
    320,
    reset=machine.Pin(TFT_RST, machine.Pin.OUT),
    cs=machine.Pin(TFT_CS, machine.Pin.OUT),
    dc=machine.Pin(TFT_DC, machine.Pin.OUT),
    rotation=3,
    color_order=st7789.BGR,
)

_print_y = MARGIN_Y

# Physical buttons: each line builds a machine.Pin you pass to is_pressed(...).
button_up = machine.Pin(PIN_UP, machine.Pin.IN)
button_down = machine.Pin(PIN_DOWN, machine.Pin.IN)
button_left = machine.Pin(PIN_LEFT, machine.Pin.IN)
button_right = machine.Pin(PIN_RIGHT, machine.Pin.IN)
button_B = machine.Pin(PIN_B, machine.Pin.IN)
button_A = machine.Pin(PIN_A, machine.Pin.IN)

# Three PWM outputs mix the red/green/blue LED next to the joystick.
pwm_red = machine.PWM(machine.Pin(PIN_RED), freq=1000)
pwm_green = machine.PWM(machine.Pin(PIN_GREEN), freq=1000)
pwm_blue = machine.PWM(machine.Pin(PIN_BLUE), freq=1000)

buzzer = machine.PWM(machine.Pin(PIN_BUZZER), freq=1000, duty=0)


def set_rgb_color(color_or_r, g=None, b=None):
    """
    One name: set_rgb_color(RED) or set_rgb_color("red") or set_rgb_color(OFF).
    Still supports raw RGB: set_rgb_color(255, 128, 0) or set_rgb_color((r, g, b)).
    """
    if g is None and b is None:
        c = color_or_r
        if isinstance(c, tuple) and len(c) == 3:
            r, g, b = int(c[0]), int(c[1]), int(c[2])
        elif isinstance(c, str):
            r, g, b = _LED_PALETTE.get(c.lower(), (0, 0, 0))
        else:
            r, g, b = _LED_PALETTE.get(str(c).lower(), (0, 0, 0))
    else:
        r = int(color_or_r)
        g = int(g)
        b = int(b)

    duty_red = int((r / 255) * PWM_MAX_DUTY / 255 * 1023)
    duty_green = int((g / 255) * PWM_MAX_DUTY / 255 * 1023)
    duty_blue = int((b / 255) * PWM_MAX_DUTY / 255 * 1023)
    pwm_red.duty(duty_red)
    pwm_green.duty(duty_green)
    pwm_blue.duty(duty_blue)


def rgb_off():
    pwm_red.duty(0)
    pwm_green.duty(0)
    pwm_blue.duty(0)


def play_tone(freq, duration_ms):
    if freq > 0:
        buzzer.freq(freq)
        buzzer.duty(512)
    utime.sleep_ms(duration_ms)
    buzzer.duty(0)


def is_pressed(button):
    return button.value() == 1


def tft_init(include_status_bar=False):
    """Init TFT; `include_status_bar=True` enables the bottom status strip."""
    tft.init([])
    set_status_bar_enabled(include_status_bar)
    tft_clear()


def _status_inputs():
    """Button line string + raw joystick ADC (for incremental status paint)."""
    vx, vy = joy_read()
    a = int(is_pressed(button_A))
    b = int(is_pressed(button_B))
    u = int(is_pressed(button_up))
    d = int(is_pressed(button_down))
    l = int(is_pressed(button_left))
    r = int(is_pressed(button_right))
    s0 = "A:%d B:%d U:%d D:%d L:%d R:%d" % (a, b, u, d, l, r)
    return s0, vx, vy


# Second status line layout: fixed labels, fixed-width number fields (matches old "Joy X:%d Y:%d").
_STATUS_JOY_L0 = "Joy X:"
_STATUS_JOY_L1 = " Y:"
_STATUS_JOY_VX_W = 5
_STATUS_JOY_VY_W = 5


def _status_joy_layout_y():
    """Return (x_vx, x_vy, fw) pixel positions for the two number fields on the joy line."""
    fw = getattr(font, "WIDTH", 8)
    x_vx = MARGIN_X + len(_STATUS_JOY_L0) * fw
    x_mid = x_vx + _STATUS_JOY_VX_W * fw
    x_vy = x_mid + len(_STATUS_JOY_L1) * fw
    return x_vx, x_vy, fw


def _paint_status_joy_line_full(y1, vx, vy):
    """Draw the full joy line (labels + numbers) — first paint or after strip reset."""
    x_vx, x_vy, fw = _status_joy_layout_y()
    tft.text(font, _STATUS_JOY_L0, MARGIN_X, y1, st7789.CYAN, STATUS_BG_COLOR)
    tft.text(font, "%5d" % vx, x_vx, y1, st7789.CYAN, STATUS_BG_COLOR)
    tft.text(font, _STATUS_JOY_L1, x_vx + _STATUS_JOY_VX_W * fw, y1, st7789.CYAN, STATUS_BG_COLOR)
    tft.text(font, "%5d" % vy, x_vy, y1, st7789.CYAN, STATUS_BG_COLOR)


def _paint_status_joy_line_partial(y1, old_vx, old_vy, vx, vy):
    """Redraw only the X/Y number slots when those ADC values change (no label flicker)."""
    x_vx, x_vy, fw = _status_joy_layout_y()
    wv = _STATUS_JOY_VX_W * fw
    if vx != old_vx:
        tft.fill_rect(x_vx, y1, wv, LINE_PX, STATUS_BG_COLOR)
        tft.text(font, "%5d" % vx, x_vx, y1, st7789.CYAN, STATUS_BG_COLOR)
    if vy != old_vy:
        tft.fill_rect(x_vy, y1, wv, LINE_PX, STATUS_BG_COLOR)
        tft.text(font, "%5d" % vy, x_vy, y1, st7789.CYAN, STATUS_BG_COLOR)


def update_status_bar():
    """Paint status strip; joy line updates only changed X/Y digits (labels stay put)."""
    if not _status_bar_enabled:
        return
    global _status_last
    s0, vx, vy = _status_inputs()
    y0 = STATUS_BAR_TOP + 4
    y1 = y0 + LINE_PX

    if _status_last is None:
        tft.fill_rect(0, STATUS_BAR_TOP, DISPLAY_W, STATUS_BAR_H, STATUS_BG_COLOR)
        _draw_status_separator_line()
        tft.text(font, _clip(s0), MARGIN_X, y0, st7789.YELLOW, STATUS_BG_COLOR)
        _paint_status_joy_line_full(y1, vx, vy)
    else:
        old0, old_vx, old_vy = _status_last
        if s0 != old0:
            tft.fill_rect(0, y0, DISPLAY_W, LINE_PX, STATUS_BG_COLOR)
            tft.text(font, _clip(s0), MARGIN_X, y0, st7789.YELLOW, STATUS_BG_COLOR)
        if vx != old_vx or vy != old_vy:
            _paint_status_joy_line_partial(y1, old_vx, old_vy, vx, vy)
    _status_last = (s0, vx, vy)


def draw_status_bar():
    """Force a full status strip redraw (e.g. after whole-screen clear)."""
    if not _status_bar_enabled:
        return
    global _status_last
    _status_last = None
    update_status_bar()


def _draw_status_separator_line():
    """One-pixel rule between console and status strip (re-draw after console_clear)."""
    if not _status_bar_enabled:
        return
    tft.hline(0, STATUS_BAR_TOP - 1, DISPLAY_W, STATUS_SEP_COLOR)


def console_clear():
    """Black out only the console (above status bar) and reset print cursor."""
    global _print_y
    tft.fill_rect(0, MARGIN_Y, DISPLAY_W, STATUS_BAR_TOP - MARGIN_Y, st7789.BLACK)
    _print_y = MARGIN_Y
    _draw_status_separator_line()


def tft_clear():
    """Full screen black, reset console cursor, redraw status strip if enabled."""
    global _print_y, _status_last
    tft.fill(st7789.BLACK)
    _print_y = MARGIN_Y
    _status_last = None
    if _status_bar_enabled:
        update_status_bar()


def _clip(s):
    s = str(s)
    if len(s) > MAX_LINE_CHARS:
        return s[: MAX_LINE_CHARS - 1] + "..."
    return s


def _write_console_line(text, fg):
    """Single place that draws one console line (lessons use print(), not this)."""
    tft.text(font, _clip(str(text)), MARGIN_X, _print_y, fg, st7789.BLACK)


def tft_print(*lines, title=None, fg=None, accent=st7789.CYAN):
    global _print_y, _status_last
    if fg is None:
        fg = DEFAULT_TEXT_COLOR
    tft.fill(st7789.BLACK)
    _status_last = None
    _print_y = MARGIN_Y
    if title is not None:
        _write_console_line(title, accent)
        _print_y += LINE_PX + 2
    for line in lines:
        if _print_y > PRINT_LAST_START_Y:
            break
        _write_console_line(line, fg)
        _print_y += LINE_PX
    if _status_bar_enabled:
        draw_status_bar()


def println(s="", fg=None, refresh_status=True):
    global _print_y
    if fg is None:
        fg = DEFAULT_TEXT_COLOR
    if _print_y > PRINT_LAST_START_Y:
        console_clear()
    _write_console_line(s, fg)
    _print_y += LINE_PX
    if refresh_status and _status_bar_enabled:
        update_status_bar()


def print(*args, sep=" ", fg=None):
    println(sep.join(str(a) for a in args) if args else "", fg)


def println_reset():
    console_clear()
    if _status_bar_enabled:
        update_status_bar()


def joy_read():
    global _jx, _jy
    if _jx is None:
        _jx = machine.ADC(machine.Pin(8))
        _jy = machine.ADC(machine.Pin(9))
        for a in (_jx, _jy):
            try:
                a.atten(machine.ADC.ATTN_11DB)
            except AttributeError:
                pass
    return _jx.read(), _jy.read()


def _addr_ensure():
    global _addr_np
    if _addr_np is not None:
        return _addr_np
    try:
        import neopixel
    except ImportError:
        return None
    try:
        _addr_np = neopixel.NeoPixel(_addr_pin, PHYS_ADDR_LEDS, timing=ADDR_LED_TIMING)
    except Exception:
        _addr_np = None
        return None
    return _addr_np


def _addr_flush(np):
    """Push buffer to the strip. Non-fatal so a bad write does not stop lessons."""
    if np is None:
        return
    try:
        np.write()
    except Exception:
        pass


def addr_blank():
    """Set every strip pixel to off in RAM only (no GPIO). Pair with px(...) then one addr_show()."""
    np = _addr_ensure()
    if np is None:
        return
    np.fill((0, 0, 0))


def addr_clear():
    """Turn all addressable LEDs off and push one frame to the hardware."""
    np = _addr_ensure()
    if np is None:
        return
    np.fill((0, 0, 0))
    _addr_flush(np)


def addr_hard_clear():
    """Recreate NeoPixel object, then clear/show. Helps recover from bad ring state."""
    global _addr_np
    _addr_np = None
    np = _addr_ensure()
    if np is None:
        return
    np.fill((0, 0, 0))
    _addr_flush(np)


def addr_set(i, r, g, b):
    """Set one WS2812 LED to (r, g, b). MicroPython's NeoPixel driver handles
    the RGB->GRB reorder internally, so pass channels in plain RGB order."""
    np = _addr_ensure()
    if np is None or not (0 <= i < NUM_ADDR_LEDS):
        return
    np[i] = (r, g, b)


def addr_show():
    np = _addr_ensure()
    if np is not None:
        _addr_flush(np)


def px(index, color):
    """
    Set one addressable LED by index using a color name (RED, OFF, …) or (r, g, b) tuple.
    Examples: px(0, RED)   px(3, "yellow")   px(5, (200, 100, 0))
    """
    if isinstance(color, tuple) and len(color) == 3:
        r, g, b = color
    elif isinstance(color, str):
        key = color.lower()
        r, g, b = _LED_PALETTE.get(key, _LED_PALETTE[OFF])
    else:
        r, g, b = _LED_PALETTE[OFF]
    d = ADDR_LED_DIM
    addr_set(index, r // d, g // d, b // d)


__all__ = (
    "print",
    "println",
    "println_reset",
    "tft_init",
    "set_status_bar_enabled",
    "draw_console_line_at_row",
    "tft_clear",
    "console_clear",
    "draw_status_bar",
    "update_status_bar",
    "tft_print",
    "tft",
    "font",
    "st7789",
    "utime",
    "sleep",
    "DEFAULT_TEXT_COLOR",
    "set_rgb_color",
    "rgb_off",
    "play_tone",
    "is_pressed",
    "button_A",
    "button_B",
    "button_left",
    "button_right",
    "button_up",
    "button_down",
    "joy_read",
    "addr_clear",
    "addr_hard_clear",
    "addr_blank",
    "addr_set",
    "addr_show",
    "px",
    "OFF",
    "RED",
    "GREEN",
    "BLUE",
    "YELLOW",
    "ORANGE",
    "MAGENTA",
    "CYAN",
    "WHITE",
    "PURPLE",
    "SLATE",
    "NUM_ADDR_LEDS",
    "ADDR_LED_DIM",
    "MAX_LINE_CHARS",
    "PRINT_LAST_START_Y",
    "STATUS_BAR_TOP",
    "STATUS_BAR_H",
    "LINE_PX",
    "MARGIN_X",
    "MARGIN_Y",
    "DISPLAY_W",
    "DISPLAY_H",
    "builtins",
)
