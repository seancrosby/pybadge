# Shared MicroPython files (board v4.1)

GPIO numbers match v4.0 for the display, buttons, joystick, and LEDs. Copy these onto the badge with any example that imports `board_v4`:

- `board_v4.py` — pins, TFT console, buttons, RGB, addressable LEDs
- `st7789py.py` — ST7789 driver
- `vga1_8x16.py` (preferred) or `vga1_8x8.py`
- `boot.py` — optional; runs at reset

VMain on v4.1 uses a 150 kΩ / 10 kΩ divider (×16). Use the `vmain` example in this `code_for_board_v4_1` folder, not the v4.0 copy.

USB keyboard and mouse host is Arduino-only.
