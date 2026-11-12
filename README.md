# pybadge

`pybadge` is a beginner-friendly Python interface for BYU-Idaho's ESP32-S3
eBadge. The goal is for any user to write ordinary Python programs that use
buttons, LEDs, the screen, sound, sensors, and Wi-Fi without dealing with GPIO
numbers or low-level electronics APIs.

The intended `pybadge.py` interface will support three modes: the physical
eBadge, an interactive terminal simulator, and a headless test backend. The
public API has been reviewed; implementation details and remaining tasks are
tracked in [TODO.md](TODO.md) and the [specifications](specifications/). The
programs in [`examples/`](examples/) show the intended user experience and
will become runnable when the API is implemented. The simulator's blue board
artwork will carry the BYU-Idaho logo permanently, separate from the simulated
screen, whose contents are controlled by the running program.

## Classroom workflow

Use this repository as the maintained source for the library, examples, and
setup instructions. Keep personal programs under `examples/` or a clearly
named work folder; normal use should not require editing library internals.
Users can fork or clone the repository when GitHub access is available. For
restricted or offline environments, distribute a ZIP or prepared checkout.
After the initial copy, programs can be developed without network access.

Record a known repository revision when reproducibility matters. Keep personal
programs and generated files separate from maintained library changes. The API
is still under implementation, so this project does not currently require a
pip package. Once the API is stable, a versioned host-side package may be an
additional simulator installation option; badge deployment will still require
copying MicroPython-compatible files to the device. See the
[user workflow recommendation](specifications/user-workflow.md) for the
distribution tradeoffs.

The first API includes accelerometer and battery-voltage helpers. Battery
readings are voltages, not estimated charge percentages. BLE and SD-card
support are deferred future work.

The terminal simulator focuses on buttons, the screen, LEDs, and buzzer
activity. It is not a full electrical or wireless simulation; the README and
simulator should identify features such as voltage measurement and Wi-Fi
scanning that are not modeled there.

## Board photographs

These V4.1.1 photos show the current target board. The front shows the controls
and components; the back includes a printed quick reference for GPIOs and buses.

![Front of the BYU-Idaho eBadge V4.1.1](byui-ebadge-front-4_1_1.jpg)

![Back of the BYU-Idaho eBadge V4.1.1](byui-ebadge-back-4_1_1.jpg)

## Repository structure

| Path | Purpose |
| --- | --- |
| `pybadge.py` | Planned user-facing API shared by all runtime modes. |
| `backends/` | Planned hardware, simulator, and test implementations. |
| `board/` | Planned e-badge Git submodule and hardware design source. |
| `specifications/` | Python standards and the current V4.1.1 board specification. |
| `examples/` | Small programs demonstrating the planned API. |
| `old/python/` | Archived course samples and hardware libraries. These are reference examples and do not follow this project's Python standards. |
| `hardware/ebadge/` | eBadge setup guide and reference material. |
| `byui-cse.png` | Logo asset used by the display example. |

The current board target is V4.1.1. The hardware specification compares the
V4 course software with the V4.1.1 design files, production netlist, and board
photos. Firmware-dependent behavior and ADC calibration are called out where
they still need validation on physical hardware.

### Board labels, GPIO numbers, and jumper bridges

The board silkscreen uses labels such as `IO13`; these identify the same signal
as ESP32 `GPIO13`. They are GPIO numbers, not physical lead numbers on the
ESP32 module. Code and pin helper functions use the ESP32 GPIO number. For
example, board label `IO13` corresponds to GPIO value `13`.

The board has removable jumper bridges that connect onboard devices and
headers to GPIO signals. The board specification and built-in peripheral
helpers describe the standard, as-built bridge positions. Removing or moving a
bridge changes the electrical routing: a built-in device may no longer be
connected to the GPIO its helper expects, and a GPIO may become available for
an external circuit. The software cannot detect a manually changed bridge, so
record any nonstandard wiring and configure the software for that wiring.

The V4.1.1 upstream production netlist confirms GPIO13–GPIO18 are routed to
J9's odd-numbered contacts (1, 3, 5, 7, 9, and 11). The upstream BOM's U1
description says `ESP32-S2-MINI-1`, while its manufacturer part number and the
design files identify an ESP32-S3-MINI-1-N4R2. Use the GPIO signal names in
software; do not infer module pad numbers from that inconsistent description.

The planned `set_pwm(pin, frequency_hz, duty_percent)` helper uses a duty
percentage from 0 to 100. A duty of `0` keeps the output off; `100` keeps it
on. For example, this requests a 1,000 Hz signal that is on half of each cycle:

```python
pybadge.set_pwm(pybadge.GPIO13, frequency_hz=1000, duty_percent=50)
```

The small RGB LED and the addressable LED strip have separate names. The
agreed API uses `set_rgb_led(color)` for the small indicator and
`set_led_strip_pixel(index, color)`, `set_led_strip(colors)`, and
`clear_led_strip()` for the 24-pixel strip. For an animation, a program can
update a whole frame in a loop and control the frame delay itself:

```python
pybadge.set_led_strip(frame_colors)
pybadge.pause(80)  # wait 80 milliseconds before the next frame
```

Frame updates and timing are separate; animations do not require a predefined
animation or a timing list.

The upstream eBadge source is tracked as a Git submodule. Initialize it after a
fresh checkout with:

```sh
git submodule update --init --recursive
```

The V4.1.1 KiCad design is in
[`board/hardware v4.1.1/badge-esp32-s3/`](<board/hardware v4.1.1/badge-esp32-s3/>).

## Set up MicroPython on the eBadge

The badge uses an ESP32-S3. Connect the computer to the badge's USB-C port
labeled **USB-UART** with a data-capable cable. Install the host tools:

```sh
python -m pip install esptool mpremote
```

Find the serial port assigned to the badge:

- **Windows:** a port such as `COM3` in Device Manager under **Ports (COM & LPT)**.
- **macOS:** usually `/dev/cu.usbmodem...` or `/dev/cu.usbserial...`.
- **Linux:** usually `/dev/ttyACM0` or `/dev/ttyUSB0`; your account may need serial-device permissions.

Download a MicroPython firmware build for a generic ESP32-S3 from the
[MicroPython ESP32-S3 downloads](https://micropython.org/download/ESP32_GENERIC_S3/).
The course setup guide refers to `ESP32_GENERIC_S3-20260824-v1.29.0.bin`, but
that binary is not currently present in this checkout. Use the filename of the
firmware image you downloaded in the command below.

Erase the badge flash and install the firmware (replace `<PORT>` and the image
filename with the values for your computer):

```sh
python -m esptool --port <PORT> erase_flash
python -m esptool --port <PORT> --baud 460800 write_flash 0 ESP32_GENERIC_S3-20260824-v1.29.0.bin
```

If the board does not enter download mode, hold **BOOT** while starting the
flash operation, then release it once flashing begins. Check the installed
`esptool` help if its command syntax differs from these course-guide commands.

Open the MicroPython REPL (interactive prompt):

```sh
python -m mpremote connect <PORT>
```

At the `>>>` prompt, try `print("Hello from the eBadge!")`. Press **Ctrl-]** to
leave the REPL. If port auto-detection works, `python -m mpremote` can connect
without an explicit port.

## Run the headless tests

The pytest suite uses the deterministic test backend. It does not launch the
terminal simulator or require an eBadge:

```sh
python -m pip install pytest
python -m pytest
```

GitHub Actions runs this suite automatically on every push and pull request.
The tests are collected only from `tests/`; archived examples under `old/` are
reference material, not pytest test modules.

## Run the examples

The four programs in [`examples/`](examples/) demonstrate the intended API:

1. Light the RGB LED while button A is held.
2. Scan for and list nearby Wi-Fi networks.
3. Play a tone when button A is pressed.
4. Display the BYU-Idaho CSE logo from `byui-cse.png`.

These programs depend on `pybadge.py`, which is not implemented yet. Their
required functions and the backend design are being tracked in [TODO.md](TODO.md).
Before running the logo example, prepare the PNG for the display with the
planned host utility:

```sh
python resize_image.py byui-cse.png
```

The utility is not implemented yet. Its planned output is a 24-bit BMP sized
for the 320 × 240 screen.

### Copy project files to the badge

The intended badge destinations are `/pybadge.py` for the shared API,
`/main.py` for the program that should start on reset, and
`/byui-cse_badge.bmp` for the prepared image used by the logo example. From the
repository root, these `mpremote` commands copy those files (replace `<PORT>`
with the badge's serial port):

```sh
python -m mpremote connect <PORT> fs cp pybadge.py :pybadge.py
python -m mpremote connect <PORT> fs cp examples/01_button_led.py :main.py
python -m mpremote connect <PORT> fs cp byui-cse_badge.bmp :byui-cse_badge.bmp
```

Copy the image only for programs that use it. To install the logo example
instead of the button example, use its filename in the second command:

```sh
python -m mpremote connect <PORT> fs cp examples/04_display_logo.py :main.py
```

The hardware backend and its support-file requirements are not implemented
yet, so these commands describe the intended destinations and are not a
complete runnable deployment procedure. Finalize the file list and any
additional copy commands with the hardware backend; see [TODO.md](TODO.md).

### Joystick values

The planned `pybadge.joystick()` function returns a tuple `(x, y)`, with each
axis ranging from `-1.0` to `1.0`. For example:

```python
x, y = pybadge.joystick()
```

For `x`, `-1.0` means fully left and `1.0` fully right. For `y`, `-1.0`
means fully down and `1.0` fully up. Values near zero mean the stick is near
the center. These are normalized direction values, not raw voltage or ADC
readings. A small center dead zone may report exactly `0.0` to make the stick
easier to use.

For examples from the earlier course materials, see [`old/python/`](old/python/)
and the archived [eBadge setup guide](hardware/ebadge/README.md). Those samples
use their own board libraries and are retained as references.

## Specifications and contribution notes

- [User repository workflow recommendation](specifications/user-workflow.md)
- [Python software specification](specifications/python.md)
- [eBadge V4.1.1 hardware specification](specifications/hardware-v4.1.1.md)
- [Project instructions](AGENTS.md)
- [Open tasks](TODO.md)

Python standards in the software specification apply to new project code. Do
not reformat the examples in `old/python/` or upstream files in `board/` to
match those standards.
