# Getting Started with MicroPython on the E-Badge

This guide explains how to set up the BYU-Idaho E-Badge, which uses an ESP32-S3, and copy and run the Python examples in this folder.

## What you need

- An E-Badge and a USB-C data cable. Connect the cable to the badge's left USB-C port, labeled **USB-UART**.
- Python 3 and `pip` installed on your computer.
- The tools used to flash firmware and manage files on the badge:

  ```sh
  pip install esptool
  pip install mpremote
  ```

On some systems, use `pip3` instead of `pip`. These examples use `python -m esptool` and `python -m mpremote`, which work across Windows, macOS, and Linux when the packages are installed for that Python interpreter.

### Find the serial port

The port name depends on your operating system. Connect the badge and look for the newly appearing serial device:

- **Windows:** a name such as `COM3` or `COM4`. Check Device Manager under **Ports (COM & LPT)**.
- **macOS:** usually `/dev/cu.usbmodem...` or `/dev/cu.usbserial...`.
- **Linux:** usually `/dev/ttyACM0` or `/dev/ttyUSB0`. Your user may need permission to access serial devices.

Replace `<PORT>` in the examples below with the port name for your computer. If automatic port detection works, you can omit the explicit port for `mpremote` commands.

## Install MicroPython

The `esp-files` folder contains the ESP32-S3 firmware used for this course: [`ESP32_GENERIC_S3-20260824-v1.29.0.bin`](esp-files/ESP32_GENERIC_S3-20260824-v1.29.0.bin). The generic ESP32-S3 firmware supports most ESP32-S3 boards with at least 4 MiB of flash. If using a different board or firmware, check the [MicroPython ESP32-S3 downloads](https://micropython.org/download/ESP32_GENERIC_S3/) and select the build appropriate for the board.

1. Connect the badge to the USB-UART port.
2. Find the serial port assigned by your computer as described above.
3. Erase the existing flash:

   ```sh
   python -m esptool erase_flash
   ```

   If esptool does not find the badge automatically, specify its port: `python -m esptool --port <PORT> erase_flash`.

4. Write the bundled firmware to the board:

   ```sh
   python -m esptool --baud 460800 write_flash 0 ESP32_GENERIC_S3-20260824-v1.29.0.bin
   ```

   If needed, add `--port <PORT>` after `--baud 460800`. Run the flash command from the directory containing the `.bin` file, or replace the filename with its path (for example, `esp-files/ESP32_GENERIC_S3-20260824-v1.29.0.bin`). If the board does not enter download mode automatically, hold its **BOOT** button while starting the flash operation, then release it once flashing begins.

## Connect to the MicroPython prompt

With the badge connected, open the ESP32 console with:

```sh
python -m mpremote
```

This opens the MicroPython REPL (interactive console). If you need to select the badge's serial port explicitly, use:

```sh
python -m mpremote connect <PORT>
```

For example, on Windows the command could be `python -m mpremote connect COM3`; on macOS or Linux, replace `COM3` with the matching `/dev/...` port path.

At the `>>>` prompt, try a simple command:

```python
print("Hello from the E-Badge!")
```

Press **Ctrl-]** to exit the prompt. The `mpremote` commands below can also be run as `python -m mpremote ...` if `mpremote` is not available as a standalone command.

## Copy and run a Python file

The example programs are in [`old/python/`](../../old/python/). From the repository root, run a file directly from your computer without copying it to the badge with:

```sh
mpremote connect auto run old/python/01_variables_and_types.py
```

### Copy the badge libraries

Some E-Badge programs need library modules saved on the board. For the beginner-friendly `ebadge.py` interface, copy it with the board support module and display dependencies:

```sh
python -m mpremote cp old/python/ebadge.py :ebadge.py
python -m mpremote cp old/python/board_v4.py :board_v4.py
python -m mpremote cp old/python/st7789py.py :st7789py.py
python -m mpremote cp old/python/vga1_8x16.py :vga1_8x16.py
```

Or, for programs that use the lower-level interface, copy the board library with:

```sh
python -m mpremote cp old/python/board_v4.py :board_v4.py
python -m mpremote cp old/python/st7789py.py :st7789py.py
python -m mpremote cp old/python/vga1_8x16.py :vga1_8x16.py
python -m mpremote cp old/python/vga1_8x8.py :vga1_8x8.py
```

Copy any other library modules a program imports the same way, using the source filename and the destination filename after `:`.

### Run a Python file

From the repository root, run a program such as `game_snake.py` on the connected badge with:

```sh
python -m mpremote run old/python/game_snake.py
```

To make `game_snake.py` run automatically whenever the badge starts, copy it from `old/python/` onto the badge as `main.py`:

```sh
python -m mpremote cp old/python/game_snake.py :main.py
```

MicroPython runs `main.py` when the badge boots. To start the script now, reset the badge or run:

```sh
mpremote connect auto reset
```

To copy a file under its original name instead, use for example:

```sh
mpremote connect auto fs cp old/python/game_tetris.py :game_tetris.py
```

Then open the REPL and run it with `import game_tetris` (omit the `.py` extension). The `boot.py` file in `old/python/` is intended for startup configuration; copy it to the device as `boot.py` only when you want that configuration to run on every boot.

## Python files and examples

The `old/python/` directory contains the course lessons, badge support modules, and demos. The examples are designed for the BYU-Idaho eBadge v4 and use MicroPython.

### Badge support modules

- [`ebadge.py`](../../old/python/ebadge.py) provides a beginner-friendly interface that hides the board and screen-driver details. Call `initialize()` before using the LCD. Its functions are grouped here:
  - **Inputs and outputs:** `is_pressed(button)`, `joystick()`, `set_led(color)`, `turn_led_off()`, `play_tone(frequency, duration_ms)`, `pause(milliseconds)`, `set_pixel(index, color)`, `clear_pixels()`, `configure_pin(number, mode, pull=None)`, `read_pin(number)`, `write_pin(number, value)`, `read_battery()`, and `read_accelerometer()`.
  - **Screen:** `display_clear(color=BLACK)`, `display_text(text, x=8, y=8, color=WHITE)`, `draw_pixel(x, y, color=WHITE)`, `draw_line(x1, y1, x2, y2, color=WHITE)`, `draw_rectangle(x, y, width, height, color=WHITE, filled=False)`, and `display_image(path, x=0, y=0, max_width=320, max_height=240)`. Images must be uncompressed 24-bit BMP files; they are proportionally shrunk to fit the given bounds.
  - **Wireless:** `connect_wifi(name, password, timeout_ms=15000)`, `disconnect_wifi()`, `download_url(url, filename=None)`, `start_bluetooth()`, `scan_bluetooth(duration_ms=4000)`, `connect_bluetooth(address, address_type=0, timeout_ms=10000)`, and `stop_bluetooth()`. Bluetooth support depends on the installed firmware; this interface uses Bluetooth Low Energy (BLE). `scan_bluetooth()` returns `(address, address_type, signal_strength)` entries; pass an entry to `connect_bluetooth(entry)`. `download_url` requires `urequests` (or `requests`) on the badge.
  - **Files and SD card:** `initialize_sd_card(sck, mosi, miso, chip_select, mount_point="/sd")`, `sd_card_present(...)`, `list_files(path="/sd")`, `read_file(path)`, `write_file(path, contents)`, `read_bytes(path)`, `write_bytes(path, contents)`, and `unmount_sd_card(mount_point=None)`. Supply the actual SD slot pin wiring for the badge revision when initializing; the course files do not define that mapping.

  Buttons are `button_a`, `button_b`, `button_up`, `button_down`, `button_left`, and `button_right`. External GPIO helpers accept pins 13–18, which must be wired to the badge's exposed header. Use 3.3 V logic. Color names include `BLACK`, `WHITE`, `RED`, `GREEN`, `BLUE`, `YELLOW`, `ORANGE`, `MAGENTA`, `CYAN`, and `PURPLE`.

- [`board_v4.py`](../../old/python/board_v4.py) provides a simple interface to the badge hardware. Import it with `from board_v4 import *`, then call `tft_init()` to initialize the display. Its `print(...)` writes text to the badge's TFT console; use `builtins.print(...)` to write to the USB serial console. `println_reset()` clears the console, while `tft_clear()` clears the whole screen. Pass `include_status_bar=True` to `tft_init()` to show a live status strip with the six button states and raw joystick X/Y readings.
- Buttons are exposed as `button_A`, `button_B`, `button_up`, `button_down`, `button_left`, and `button_right`. Use `is_pressed(button_A)` to read a button. `joy_read()` returns the raw `(x, y)` joystick ADC readings.
- Screen helpers include `print`, `println`, `tft_print`, `console_clear`, `tft_clear`, and `set_status_bar_enabled`. Hardware output helpers include `set_rgb_color(...)` / `rgb_off()` for the RGB LED, `play_tone(frequency, duration_ms)` for the buzzer, and `sleep(milliseconds)` for pauses.
- The 24 addressable LEDs can be controlled with `px(index, color)` or the lower-level `addr_blank()`, `addr_set(index, r, g, b)`, and `addr_show()` functions. `addr_clear()` turns the full ring off. Named colors such as `RED`, `CYAN`, and `YELLOW` are available.
- [`st7789py.py`](../../old/python/st7789py.py) is the ST7789 TFT display driver used by `board_v4.py` and the graphical demos. It defines the `ST7789` display class and drawing operations such as text, fills, and lines.
- [`vga1_8x16.py`](../../old/python/vga1_8x16.py) and [`vga1_8x8.py`](../../old/python/vga1_8x8.py) provide the bitmap fonts used by the display driver. `board_v4.py` prefers the 8x16 font and falls back to 8x8.

### Lessons

- [`00_input_status.py`](../../old/python/00_input_status.py) displays live button and joystick readings, accelerometer measurements when the sensor is available, and the raw battery ADC reading.
- [`01_variables_and_types.py`](../../old/python/01_variables_and_types.py) introduces strings, integers, floats, booleans, and basic value updates and calculations.
- [`02_conditionals.py`](../../old/python/02_conditionals.py) demonstrates comparisons and Boolean logic by driving addressable LEDs from button and joystick conditions.
- [`03_if_else_chain.py`](../../old/python/03_if_else_chain.py) demonstrates `if` / `elif` / `else` using buttons and the RGB LED.
- [`04_loops.py`](../../old/python/04_loops.py) demonstrates `for` and `while` loops with the buzzer, LED ring, and RGB LED.
- [`05_functions.py`](../../old/python/05_functions.py) demonstrates defining functions, parameters, return values, and functions that perform actions.
- [`06_lists.py`](../../old/python/06_lists.py) demonstrates list indexing, list traversal, and selecting colors with the left/right buttons.

### Demos, games, and startup

- [`demo_piano.py`](../../old/python/demo_piano.py) is a six-button piano built with `ebadge.py`. Hold A, B, Up, Down, Left, or Right to play a note; the screen names the note and the addressable LED ring lights up. Copy `demo_piano.py` to the badge and run it with `python -m mpremote run demo_piano.py` after copying the badge libraries above.
- [`byui_demo.py`](../../old/python/byui_demo.py) shows a BYU-Idaho splash screen and cycles through blue-and-white addressable LED patterns. Press B to exit.
- [`demo_wireless_scan.py`](../../old/python/demo_wireless_scan.py) scans for nearby Wi-Fi networks and Bluetooth LE advertisers when the installed firmware supports those features. Press A for Wi-Fi, B for BLE, or both for a full cycle.
- [`game_etch_sketch.py`](../../old/python/game_etch_sketch.py) is an Etch-a-Sketch drawing program controlled by the joystick and buttons.
- [`game_snake.py`](../../old/python/game_snake.py) is a Snake game controlled with the badge inputs.
- [`game_tetris.py`](../../old/python/game_tetris.py) is a Tetris game controlled with the badge inputs.
- [`boot.py`](../../old/python/boot.py) draws a menu of Python scripts on the badge and lets you select and run them with the buttons or joystick. Copy it to the device as `boot.py` only if you want it to run at startup.
- [`python_files-2026-10-21.zip`](../../old/python/python_files-2026-10-21.zip) is an archive of the course Python files.

The files are also available from the `old/python/` directory for copying to the badge; see the setup instructions above for `mpremote` commands. `esp-files/` contains the ESP32-S3 MicroPython firmware image, and `assignment.html` and `prepare-copy-and-run.html` are course activity pages.

## Troubleshooting

- **No serial port appears:** Confirm that the cable supports data, use the USB-UART port, and try another USB port. Some systems may also require a USB-to-serial driver for the badge.
- **Permission denied on Linux:** Add your user to the system's serial-device group or run the command with the permissions your institution recommends.
- **Flash command cannot connect:** Check the port name, close other serial terminal programs, and try holding **BOOT** while connecting or starting the operation.
- **The badge behaves unexpectedly after flashing:** Erase the flash, write the firmware again, then reconnect with `mpremote`.

## References

- [MicroPython ESP32-S3 firmware and installation notes](https://micropython.org/download/ESP32_GENERIC_S3/)
- [MicroPython ESP32 getting started guide](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)
- [MicroPython `mpremote` documentation](https://docs.micropython.org/en/latest/reference/mpremote.html)
- [esptool documentation](https://docs.espressif.com/projects/esptool/en/latest/esp32/)
