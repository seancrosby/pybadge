# eBadge hardware specification: V4.1.1 target

## Scope and evidence

This document records the board facts needed by the `pybadge.py` interface. The target hardware revision is V4.1.1. The pin assignments below are transcribed from the repository's current eBadge V4 MicroPython sample, primarily [`board_v4.py`](../hardware/ebadge/python-files/board_v4.py), and are not yet cross-checked against the V4.1.1 schematic or PCB source. The sample identifies itself as eBadge v4.0, so treat its mapping as a working reference until it is verified against `board/hardware/v4.1.1`.

The supplied [board photograph](../byui-ebadge-4_0.jpg) shows the physical arrangement. Its filename identifies it as a 4.0 image, so it documents the visible design but does not by itself prove every V4.1.1 detail. Confirm revision-specific differences from the V4.1.1 CAD files before treating this visual description as revision-certified.

## Board overview

- **Controller:** ESP32-S3 module (visible module marking in the photograph; the V4 sample targets ESP32-S3 MicroPython).
- **Display:** color TFT, driven by an ST7789 controller over SPI. The sample configures a 320 × 240 pixel logical display.
- **Inputs:** two action buttons (A and B), four directional buttons, and an analog two-axis joystick.
- **Outputs:** one RGB LED, an audible buzzer, and a ring/strip of 24 addressable LEDs.
- **Motion sensing:** the input lesson probes an MMA8451/MMA8452-compatible accelerometer over I²C at address `0x1C`.
- **Wireless:** ESP32-S3 Wi-Fi is used by the Wi-Fi scan sample. Bluetooth Low Energy scanning is demonstrated conditionally; availability depends on the installed MicroPython firmware and its `bluetooth` module/API.
- **Expansion:** exposed headers provide GPIO and power connections. The example `ebadge.py` allows GPIO 13–18 for external use and cautions that logic must not exceed 3.3 V.

## Pin assignments from current V4 software sample

The following table reflects `hardware/ebadge/python-files/board_v4.py` and `ebadge.py`; verify all rows against the V4.1.1 board design before relying on them for new hardware documentation.

| Function | ESP32-S3 GPIO | Details |
| --- | ---: | --- |
| TFT SPI clock (SCLK) | 46 | SPI bus 1 in the sample |
| TFT SPI data out (MOSI) | 3 | SPI bus 1 |
| TFT SPI data in (MISO) | 12 | SPI bus 1 |
| TFT reset | 1 | Output |
| TFT chip select (CS) | 0 | Output |
| TFT data/command (DC) | 45 | Output |
| Up button | 11 | Active-high in the sample |
| Down button | 47 | Active-high in the sample |
| Left button | 21 | Active-high in the sample |
| Right button | 10 | Active-high in the sample |
| B button | 33 | Active-high in the sample |
| A button | 34 | Active-high in the sample |
| Joystick X | 8 | ADC; sample returns raw readings |
| Joystick Y | 9 | ADC; sample returns raw readings |
| RGB LED red channel | 2 | PWM |
| RGB LED green channel | 4 | PWM |
| RGB LED blue channel | 5 | PWM |
| Buzzer | 48 | PWM |
| Addressable LED data | 7 | Sample configures 24 LEDs |
| Battery monitor | 12 | ADC; sample returns raw ADC count |
| Accelerometer SDA | 41 | I²C bus 0, 400 kHz in sample |
| Accelerometer SCL | 42 | I²C bus 0, 400 kHz in sample |
| External helper GPIOs | 13–18 | Accepted by `ebadge.configure_pin`; intended for exposed headers |

**Potential pin conflict:** the software sample assigns GPIO 12 to both TFT MISO and battery ADC. This may reflect a shared connection or a sample implementation constraint; verify the schematic and avoid assuming these uses can operate independently.

**SD card:** sample helpers contain generic SD-card initialization but explicitly do not define the slot pin mapping. Do not publish an SD pin map until it is confirmed in the target board design.

## Visual layout (as seen in `byui-ebadge-4_0.jpg`)

Orientation below is the orientation of the photograph: USB connectors along the top edge and the buttons along the lower edge.

- The **TFT screen** sits near the center of the board.
- The **joystick** is a large control on the left side of the screen.
- Four **direction buttons** (up, left, down, right) are grouped near the lower-left corner, below the joystick. The silkscreen labels `BtnU`, `BtnL`, `BtnD`, and `BtnR` identify them.
- The **A and B action buttons** are at the lower-right edge of the board, to the right of the screen; the photograph labels them `BtnA` and `BtnB`.
- **Unpopulated/exposed expansion headers** are visible along the lower edge, below the screen, and in banks near the upper left and upper right edges. Their silkscreen identifies GPIO, I²C, power, and ground connections. The exact connector-to-GPIO mapping and which pins are safe for general use must be transcribed from the V4.1.1 design files rather than inferred from the photo.
- The photo also shows USB-UART and USB-CDC connectors at the top, plus a microSD card socket on the right side. Their availability and intended MicroPython workflows should be confirmed for V4.1.1.

The image is useful for finding controls by sight, but it is a V4.0-named reference. Use the V4.1.1 PCB/schematic to settle exact header labels, mounting orientation, and any component changes.

## Capabilities and software implications

| Capability | Evidence / behavior to support |
| --- | --- |
| Buttons | Six digital inputs: A, B, up, down, left, right. Existing sample reports pressed when the GPIO reads high. |
| Joystick | Two analog axes, exposed in the sample as raw `(x, y)` ADC counts. A beginner API may add direction/center interpretation only after calibration behavior is verified. |
| Display | ST7789 TFT; 320 × 240 logical pixels in the current sample. Text and basic drawing are available through the driver. |
| RGB LED | Three PWM channels; support named colors and/or RGB values through a friendly helper. |
| Addressable LEDs | 24 LEDs on a serial data line. The sample exposes a color palette and single-pixel/ring operations. |
| Buzzer | PWM tone output with frequency in hertz and duration in milliseconds. |
| Accelerometer | I²C sensor check for MMA8451/MMA8452 ID at `0x1C`; sample reports acceleration in g when recognized. |
| Battery monitor | ADC measurement is available, but the sample only documents raw counts, not voltage or charge percentage. |
| Wi-Fi | ESP32-S3 MicroPython `network.WLAN` station interface is used for scanning and connecting. Firmware and regional radio rules may affect operation. |
| Bluetooth LE | Demonstrated via `bluetooth.BLE` and `gap_scan`; availability and exact API support depend on the firmware build. |
| External GPIO | GPIO 13–18 are accepted by the sample helper for exposed external connections; use 3.3 V logic and confirm header wiring before connecting hardware. |
| SD storage | Generic initialization helpers exist, but badge slot wiring is unspecified in the examples. Treat as unsupported until V4.1.1 wiring and firmware behavior are verified. |

## Source files to verify during board setup

- `board/hardware/v4.1.1/`: authoritative target-revision layout, schematics, and component information in the upstream e-badge repository.
- `hardware/ebadge/python-files/board_v4.py`: display, button, joystick, RGB LED, buzzer, and addressable LED mapping used by the current sample.
- `hardware/ebadge/python-files/ebadge.py`: accelerometer, battery ADC, Wi-Fi/BLE, exposed GPIO, and generic SD helper behavior.
- `hardware/ebadge/python-files/demo_wireless_scan.py`: demonstrated Wi-Fi scan and conditional BLE scan behavior.
- `byui-ebadge-4_0.jpg`: visual guide to physical control and header placement; V4.0-named image, not authoritative for V4.1.1 differences.
