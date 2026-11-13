# Python software specification

## Scope

These standards apply to new project Python code, especially the user-facing `pybadge.py` module and its supporting project code. They do not apply to archived samples in `old/python/` or upstream design files kept in `board/`; those files are reference examples and should be preserved as such.

The software targets MicroPython on the ESP32-S3 eBadge. Keep the public interface approachable for learners who know Python functions but do not know electronics APIs.

`pybadge.py` has three runtime modes with one shared API: hardware mode on the physical badge, interactive simulator mode on a computer, and deterministic headless test mode for `pytest`. The simulator presents a terminal board view with clickable buttons and joystick positions; it models display, LED, and buzzer output. The test backend must not launch a UI or wait for input.

## Design principles

- Give users clear, task-oriented functions such as `is_pressed(...)`, `set_rgb_led(...)`, and `display_text(...)`. Keep GPIO numbers, peripheral setup, and driver objects inside the library unless a feature explicitly exposes them.
- Use small functions with one clear purpose and predictable inputs, return values, and side effects.
- Keep hardware initialization deliberate. Document which functions initialize hardware automatically and which require an explicit `initialize()` call.
- Prefer consistent names and behavior across related helpers. Use lower-case `snake_case` for functions and variables, and uppercase names for constants.
- Use descriptive names rather than unexplained abbreviations. Follow established names only when matching an external hardware API.

## Readability and documentation

- Use four spaces for indentation and keep lines reasonably short (aim for 88 characters where practical).
- Add a module docstring describing the module's purpose and a short usage example.
- Add docstrings to public functions. Describe parameters, return values, units, expected board state, and exceptions when those details are not obvious.
- Use comments to explain hardware constraints or non-obvious decisions, not to restate each line of code.
- Prefer straightforward control flow and avoid clever abstractions that make beginner-facing behavior harder to follow.

## MicroPython compatibility

- Use the standard library and modules present in the target MicroPython firmware. Treat optional modules such as `bluetooth` and `urequests` as optional and handle their absence clearly.
- Avoid CPython-only packages, filesystem assumptions, and APIs unless they are explicitly available on the target firmware.
- Keep memory use suitable for a microcontroller. Avoid loading large resources into memory when they can be streamed or processed in small pieces.
- Use `utime` tick helpers for elapsed-time calculations that must remain correct when the tick counter wraps.
- Keep hardware-dependent imports and setup organized so unsupported features can fail with a useful, understandable error rather than an obscure import or pin exception.

## Inputs, outputs, and errors

- Validate public arguments at the API boundary. Reject invalid values with a clear `TypeError` or `ValueError` where appropriate.
- Use consistent units in names and documentation (`duration_ms`, `frequency_hz`, and screen coordinates in pixels, for example).
- Return useful values for read operations and document their scale. Do not imply that raw ADC values are percentages or calibrated physical units.
- Do not silently convert invalid color names, pins, or modes into unrelated valid settings. Make unsupported inputs visible to the learner.
- Avoid catching broad exceptions unless the API can provide a useful fallback or clearer error. Preserve enough error context to help diagnose hardware and firmware issues.

## Hardware safety and resource use

- Do not expose a pin-level operation without documenting which pins are safe for that use and the applicable voltage limits.
- Avoid reconfiguring GPIOs already used by built-in board components.
- Release or disable resources such as PWM outputs, radio interfaces, and mounted storage when a public operation owns their lifecycle and can do so safely.
- Document firmware-dependent features such as Bluetooth Low Energy and optional network libraries.

## Example and review expectations

- Keep examples short and runnable on the supported badge firmware.
- Prefer examples that introduce one concept at a time and use `pybadge.py` instead of low-level `machine` calls.
- When changing an API, update its docstring and the project README or relevant specification so they describe the same behavior.
- Review new project code for MicroPython compatibility, clear failure behavior, and unintended interaction with board peripherals.

## User program organization

- Keep the shared library and backend implementation separate from user programs. Place adaptable programs in `examples/` or a clearly named work directory; normal use should not require changing library internals.
- Examples should be short, runnable demonstrations of the public API and should state any required files or setup. Keep them suitable for copying to the badge as individual MicroPython programs.
- The repository source is the initial distribution format. Users may fork/clone it or use a prepared ZIP/checkout; instructions should name a revision when reproducibility matters. Do not add packaging-specific complexity to the MicroPython library solely to support distribution.
