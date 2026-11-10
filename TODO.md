# Project task list

## Completed

- [x] Add project instructions in `AGENTS.md`.
- [x] Add Python and V4.1.1 hardware specification drafts under `specifications/`.
- [x] Archive the course examples under `old/python/` without applying project Python standards to them.
- [x] Add beginner-facing example programs under `examples/`.

## Project structure and documentation

- [x] Create the top-level README with the repository map, usage instructions, embedded `byui-ebadge-4_0.jpg`, and MicroPython installation steps adapted from `hardware/ebadge/README.md`.
- [x] Add the BYU-I eBadge repository (`git@github.com:BYU-I-eBadge/e-badge.git`) as a Git submodule under `board/`.
- [ ] Create documented command lists or scripts using `mpremote` to copy required libraries and student program files to the eBadge, including the expected destination filenames and paths.
- [x] Review the V4.1.1 hardware design and merge useful findings from `specifications/board_info_v4_1.md` into `specifications/hardware-v4.1.1.md`, including verified pin mappings, SD wiring, jumperable power sensing, wireless capability, and API candidates. Keep firmware-dependent details and ADC calibration clearly qualified.
- [ ] Commit the staged archive move and related documentation changes so the archived source files are recorded in Git history.

## `pybadge.py` and runtime modes

- [x] Review the public API with the project owner; agreed decisions are recorded in [`specifications/api-proposal.md`](specifications/api-proposal.md).
- [ ] Implement one stable, beginner-friendly `pybadge.py` API backed by three modes:
  - [ ] Hardware mode: delegate to a board-specific hardware library on the eBadge.
  - [ ] Simulator mode: run on a regular computer with a terminal board visual, simple display, and clickable buttons. Evaluate Textual or Rich for the interface.
    - [ ] Put the BYU-Idaho logo in the blue board artwork as permanent silkscreen-style decoration, separate from the program-controlled simulated screen. Provide a terminal-compatible fallback when image rendering is unavailable.
    - [ ] Focus the simulator on buttons, screen, LEDs, and buzzer; clearly document unsupported simulation such as Wi-Fi, ADC voltage readings, and full electrical behavior.
  - [ ] Test mode: a deterministic, headless backend for `pytest`; it must not start the terminal interface or wait for input.
- [ ] Define backend selection and initialization without import-time hardware or UI side effects. Keep shared API behavior consistent across modes.
- [ ] Implement the functions used by `examples/` (button reads, LED output, Wi-Fi scanning, tones, display text/image) in all applicable backends.
- [ ] Implement accelerometer readings in g and battery-voltage readings in volts in applicable backends. Do not describe battery voltage as a charge percentage.
- [ ] After API review, implement external GPIO input/output helpers, `HIGH`/`LOW` checks, PWM output, analog voltage measurement, and addressable LED strip controls in each applicable backend. Use GPIO13–GPIO18 (`IO13`–`IO18` on the board) and verify which have analog input support.
- [ ] Document the standard jumper-bridge routing assumed by built-in peripheral helpers, and define how users configure software when they change the physical bridges.
- [ ] Create a host-side `resize_image.py` utility that accepts common PNG/JPG inputs, preserves aspect ratio, fits them to the 320 × 240 badge display, and outputs a 24-bit BMP supported by the hardware image helper.
- [ ] Track `byui-cse.png`, generate its prepared BMP with `resize_image.py`, and document how to copy that resource to the badge before running the logo example.

## Tests

- [ ] Add `pytest` unit tests for `pybadge.py` using the headless test backend. Cover button state, LED state, tone requests, Wi-Fi results, display operations, and backend selection.
- [ ] Add interactive hardware test programs for the `pybadge.py` public API. Include button checks, RGB and addressable LED checks, buzzer tone checks, display checks, and Wi-Fi scanning where supported.
- [ ] Add interactive hardware test programs for the hardware-specific interface itself, independently of `pybadge.py`, covering the same physical components where practical.
- [ ] Include accelerometer and battery-voltage checks in headless and interactive hardware validation. These are not required in the focused terminal simulator.
- [ ] Document how to run automated tests on a computer and how to run/interpret the interactive checks on the physical badge.

## Example programs

- [x] Example 1: light an LED while a button is pressed (`examples/01_button_led.py`).
- [x] Example 2: list nearby Wi-Fi networks (`examples/02_list_wifi.py`).
- [x] Example 3: play a note when a button is pressed (`examples/03_button_tone.py`).
- [x] Example 4: display the BYU-Idaho logo from a prepared display image (`examples/04_display_logo.py`).

## Deferred future work

- [ ] Add Bluetooth Low Energy (BLE) support after the target MicroPython firmware's `bluetooth.BLE` and `gap_scan` behavior is verified on the badge.
- [ ] Add SD-card support after SPI/SD mounting, filesystem behavior, and safe unmounting are verified with the target MicroPython firmware. V4.1.1 wiring is documented as GPIO37–40.
- [ ] Validate `read_battery_voltage()` on physical hardware; V4.1.1 uses a 150 kΩ / 10 kΩ divider (nominal ×16), but ADC conversion needs calibration and the signal measures the selected `PWR_RAW` rail.
- [ ] Evaluate later API additions from the V4.1 examples: servo control, display drawing primitives, UART helpers, accelerometer events, and higher-level song playback.
