# boot.py — MicroPython launcher for e-Badge v4 (copy with lessons + board_v4 + drivers to device).
#
# What this file does (big picture):
#   1. Figures out which folder it lives in and adds that folder to sys.path so imports work.
#   2. Turns off RGB LED, addressable ring, and buzzer (clean state after REPL or a crash).
#   3. Scans for .py lesson files (skipping libraries like board_v4.py).
#   4. Draws a menu on the screen. You move the highlight with Up/Down (buttons or
#      joystick Y) and press A to run the selected script.
#   5. When the script finishes, you come back to the menu and the loop repeats forever.
#
# Copies to the board root (same folder as board_v4.py, st7789py.py, lesson *.py).
# Runs first on boot; then main.py runs if present. This file loops forever as a menu,
# so remove or rename main.py if you only want this launcher (or put a one-line main.py
# that imports nothing).
#
# Up / Down (buttons or joystick): move highlight   A: run selected script

import gc
import sys

# MicroPython sets __file__ to the path of this script. We need the folder name so
# we can load board_v4 and lessons from the same place (SD card or flash).
try:
    _f = __file__
    if "/" in _f:
        _ROOT = _f.rsplit("/", 1)[0]
    else:
        _ROOT = "."
except NameError:
    _ROOT = "."


def _fullpath(name):
    """Turn a short filename into a path relative to the folder boot.py lives in."""
    if _ROOT in ("", "."):
        return name
    return _ROOT.rstrip("/") + "/" + name


# Python only looks in certain folders for imports; make sure our lesson folder is first.
_p = _ROOT if _ROOT not in ("", ".") else "."
if _p not in sys.path:
    sys.path.insert(0, _p)

from board_v4 import (
    DEFAULT_TEXT_COLOR,
    MAX_LINE_CHARS,
    addr_blank,
    addr_clear,
    addr_hard_clear,
    addr_set,
    addr_show,
    buzzer,
    draw_console_line_at_row,
    is_pressed,
    button_A,
    button_down,
    button_up,
    joy_read,
    play_tone,
    println_reset,
    print,
    rgb_off,
    set_status_bar_enabled,
    st7789,
    tft_clear,
    tft_init,
    utime,
)

# Clear RGB and buzzer in case REPL or a crashed script left them on.
# NOTE: avoid writing the addressable ring here; some firmware/boards can hang
# during very-early NeoPixel writes before the menu is up.
try:
    rgb_off()
except Exception:
    pass
try:
    buzzer.duty(0)
except Exception:
    pass

# Filenames we never show in the menu (support code, not a lesson you run by itself).
SKIP_NAMES = frozenset(
    {
        "0.py",
        "boot.py",
        "board_v4.py",
        "st7789py.py",
        "vga1_8x8.py",
        "vga1_8x16.py",
    }
)
PINNED_FIRST_SCRIPT = "byui_demo.py"

# Wait this long after a menu move before accepting another (stops one press from skipping many lines).
MENU_DEBOUNCE_MS = 220
_TITLE_LINES = 2
# Joystick Y for menu: physical up increases ADC on this board (invert vs naive low=up).
_JOY_CENTER = 2048
_JOY_EDGE = 450


def _menu_visible_lines():
    """How many script lines fit under the title, using the full TFT height (boot has no status bar).

    We use DISPLAY_H and LINE_PX read from board_v4 at call time. Do not use
    PRINT_LAST_START_Y from a static import — it was captured while the lesson layout
    still assumed a status bar, which made the menu think fewer lines fit.
    """
    import board_v4 as bv

    lp = bv.LINE_PX
    my = bv.MARGIN_Y
    dh = bv.DISPLAY_H
    # Row r starts at my + r*lp; bottom pixel of that row is my + (r+1)*lp - 1, must stay < dh.
    rows_total = (dh - my) // lp
    return max(3, rows_total - _TITLE_LINES)


def _menu_scroll_window(n_files, selected, vis):
    """Keep window=0 until the highlight reaches the bottom row; then scroll by one.

    Same when moving up: scroll only when the highlight hits the top visible row.
    """
    if n_files <= vis:
        return 0
    return max(0, min(selected - (vis - 1), n_files - vis))


def _clip_menu_label(label):
    """Shorten a filename so it fits one line on the TFT."""
    mc = MAX_LINE_CHARS - 2
    label = str(label)
    if len(label) > mc:
        return label[: max(0, mc - 3)] + "..."
    return label


def _menu_file_row(list_index, window):
    """Screen row (0-based) for files[list_index] when `window` is first visible index."""
    return _TITLE_LINES + (list_index - window)


def _paint_file_line(files, list_index, window, selected):
    """Draw one menu line: green with '>' for the selected file, white otherwise."""
    row = _menu_file_row(list_index, window)
    label = _clip_menu_label(files[list_index])
    prefix = "> " if list_index == selected else "  "
    fg = st7789.GREEN if list_index == selected else DEFAULT_TEXT_COLOR
    draw_console_line_at_row(row, prefix + label, fg)


def draw_menu_full(files, selected):
    """Clear the screen and draw the title plus every visible filename (used when the list scrolls)."""
    tft_clear()
    if not files:
        draw_console_line_at_row(0, "No .py scripts found.", DEFAULT_TEXT_COLOR)
        draw_console_line_at_row(1, "(Add lessons next to boot.py)", DEFAULT_TEXT_COLOR)
        return

    vis = _menu_visible_lines()
    window = _menu_scroll_window(len(files), selected, vis)
    window_end = min(len(files), window + vis)

    draw_console_line_at_row(0, "Select script  Up/Dn or stick  A=Run", st7789.CYAN)
    draw_console_line_at_row(1, "", DEFAULT_TEXT_COLOR)
    for i in range(window, window_end):
        _paint_file_line(files, i, window, selected)


def draw_menu_delta(files, window, old_sel, new_sel):
    """Only repaint the two rows whose selection highlight changed (same scroll window)."""
    _paint_file_line(files, old_sel, window, new_sel)
    _paint_file_line(files, new_sel, window, new_sel)


def list_scripts():
    """Return every .py filename in this folder except the ones in SKIP_NAMES."""
    import os

    root = _ROOT if _ROOT not in ("", ".") else "."
    names = []
    for n in os.listdir(root):
        if n.endswith(".py") and n not in SKIP_NAMES:
            names.append(n)
    names = sorted(names)
    if PINNED_FIRST_SCRIPT in names:
        names.remove(PINNED_FIRST_SCRIPT)
        names.insert(0, PINNED_FIRST_SCRIPT)
    return names


def _ring_off_stable():
    """Best-effort shutdown of RGB, buzzer, and addressable ring."""
    try:
        rgb_off()
    except Exception:
        pass
    try:
        buzzer.duty(0)
    except Exception:
        pass
    try:
        # WS2812 writes can occasionally glitch; do a few clears so one bad frame
        # does not leave the ring stuck on when entering the menu.
        for _ in range(3):
            addr_clear()
            utime.sleep_ms(8)
        addr_hard_clear()
        utime.sleep_ms(8)
        addr_hard_clear()
    except Exception:
        pass


def run_script(filename):
    """Read the .py file as text and run it with exec (same idea as typing it in the REPL)."""
    # Lessons expect the status strip at the bottom; turn it on before the lesson runs.
    set_status_bar_enabled(True)
    path = _fullpath(filename)
    tft_clear()
    println_reset()
    print("Running:", filename, fg=st7789.CYAN)
    play_tone(660, 80)
    utime.sleep_ms(150)

    # __name__ "__main__" is what normal Python sets when you run a file as the main program.
    g = {"__name__": "__main__", "__file__": path}
    try:
        with open(path, "r") as f:
            code = f.read()
        exec(code, g)
    except SystemExit:
        pass
    except Exception as e:
        println_reset()
        print("Error in", filename, fg=st7789.RED)
        print(str(e), fg=st7789.YELLOW)
        play_tone(200, 400)
        utime.sleep_ms(2500)

    # Free RAM, turn off LEDs, then hide the status strip again for the boot menu look.
    gc.collect()
    rgb_off()
    _ring_off_stable()
    set_status_bar_enabled(False)


def menu_loop():
    """The main program: show menu, read buttons, run scripts, repeat."""
    files = list_scripts()
    selected = 0
    prev_window = None
    prev_selected = None
    last_up = False
    last_down = False
    last_joy_up = False
    last_joy_down = False
    last_a = False
    last_nav = 0

    # Boot menu uses the full screen height (no bottom input strip).
    tft_init(include_status_bar=False)
    # Clear ring after display init (safer point than very-early boot import time).
    _ring_off_stable()
    draw_menu_full(files, selected)
    if files:
        vis = _menu_visible_lines()
        prev_window = _menu_scroll_window(len(files), selected, vis)
        prev_selected = selected

    while True:
        now = utime.ticks_ms()
        up = is_pressed(button_up)
        down = is_pressed(button_down)
        _vx, vy = joy_read()
        joy_up = vy > (_JOY_CENTER + _JOY_EDGE)
        joy_down = vy < (_JOY_CENTER - _JOY_EDGE)
        a_btn = is_pressed(button_A)

        # Menu navigation with debounce (D-pad edges or joystick pushed past neutral band).
        if files and utime.ticks_diff(now, last_nav) >= MENU_DEBOUNCE_MS:
            changed = False
            if (up and not last_up) or (joy_up and not last_joy_up):
                if selected <= 0:
                    selected = len(files) - 1
                else:
                    selected -= 1
                changed = True
                play_tone(500, 30)
            elif (down and not last_down) or (joy_down and not last_joy_down):
                if selected >= len(files) - 1:
                    selected = 0
                else:
                    selected += 1
                changed = True
                play_tone(520, 30)
            if changed:
                last_nav = now
                vis = _menu_visible_lines()
                window = _menu_scroll_window(len(files), selected, vis)
                if prev_window is None or window != prev_window:
                    draw_menu_full(files, selected)
                    prev_window = window
                else:
                    draw_menu_delta(files, window, prev_selected, selected)
                prev_selected = selected
                prev_window = window

        # "not last_a" means we only trigger once per press (edge detection for A).
        if files and a_btn and not last_a:
            run_script(files[selected])
            files = list_scripts()
            if selected >= len(files):
                selected = max(0, len(files) - 1)
            prev_window = None
            prev_selected = None
            draw_menu_full(files, selected)
            if files:
                vis = _menu_visible_lines()
                prev_window = _menu_scroll_window(len(files), selected, vis)
                prev_selected = selected
            last_nav = utime.ticks_ms()
            last_a = True
        else:
            last_a = a_btn

        last_up = up
        last_down = down
        last_joy_up = joy_up
        last_joy_down = joy_down
        utime.sleep_ms(30)


menu_loop()
