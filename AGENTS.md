# Project instructions

## Project purpose

This repository develops a user-friendly MicroPython wrapper for the BYU-Idaho eBadge. The main library is `pybadge.py`. Its public helpers should let any user work with the board without needing to understand low-level electronics or C-style hardware APIs.

## Intended repository structure

- `pybadge.py`: the user-facing helper library for supported eBadge functions.
- A hardware backend for running `pybadge.py` on the physical eBadge and a computer simulator backend for running the same programs on a regular computer.
- `board/`: board designs and code samples used as source material for hardware details. Keep the e-badge source repository here as a Git submodule; the project is currently targeting board version V4.1.1.
- `specifications/`: software and board specifications. Include Python coding standards and a board specification describing physical layout, pins, connected components, and capabilities such as Wi-Fi. Derive board facts from the materials in `board/` and cite or point to the relevant source files where practical.
- `README.md`: explain the repository, its structure, and how to set up and use the board. Embed current V4.1.1 board photos. Include the MicroPython installation instructions from `hardware/ebadge/README.md`, adapting paths to the final layout as needed.

## Distribution and user programs

- Treat this repository as the maintained source for the wrapper, examples, and setup documentation. Keep user programs in `examples/` or a clearly named work directory; normal use should not require editing library internals.
- Support Git-based copies and offline distribution as a ZIP or prepared checkout. Do not assume users have reliable network access after receiving the files.
- Instructions should identify a known revision when reproducibility matters. Keep personal programs and generated files out of the maintained library source unless they are intended project contributions.
- Do not require pip packaging as the only way to use the project. Once the API is stable, a versioned host-side package may supplement the source checkout for simulator use. Badge deployment remains a separate transfer of MicroPython-compatible files.
- Keep distribution tradeoffs in `specifications/user-workflow.md` and summarize practical setup steps in `README.md`.

## Audience and terminology

- Describe this project as a user-friendly Python wrapper for any user of the BYU-Idaho eBadge. Do not frame the repository, its API, examples, or documentation around particular education roles. Use general terms such as “user,” “program,” and “project.”

## Hardware source and version scope

- The upstream source is `git@github.com:BYU-I-eBadge/e-badge.git`, included as a Git submodule under `board/`.
- The current target is V4.1.1. Its layout is in the upstream repository's `hardware v4.1.1/` directory (the directory name contains spaces).
- Consult other upstream component information as needed. Use the archived examples under `old/python/` to identify component-to-pin mappings and demonstrated capabilities.
- The board specification must explain the visual layout of the eBadge: button locations, screen location, and empty/exposed headers. Use the V4.1.1 board photos and design materials as evidence. Distinguish confirmed facts from anything that remains uncertain.
- Preserve the existing `hardware/ebadge` materials as reference/course examples unless a task explicitly asks to change them. The archived examples in `old/python/` are reference material only.

## Python standards and examples

- Define practical Python best practices in `specifications/` for new project code, especially `pybadge.py`: readable names, small focused functions, useful docstrings, clear errors, and MicroPython compatibility.
- Apply those standards to newly developed project code. Files in `board/` are upstream designs and samples, and files in `old/python/` are archived course samples; do not reformat or otherwise impose project Python standards on them.
- Keep the user-facing API approachable and hide pin-level details when a simple helper can safely express the action.
- Keep example programs separate from implementation modules so users can adapt programs without changing the shared library. Identify a stable revision when reproducibility matters and provide an offline copy when connectivity is uncertain.

## Cross-platform runtime and simulator

- `pybadge.py` must expose the same beginner-friendly API in three runtime modes: physical hardware, interactive computer simulator, and headless test backend. Example programs should work in hardware and simulator modes without hardware-specific changes.
- In hardware mode, delegate operations to an underlying library that interfaces with the eBadge hardware. In simulator mode, use a terminal visual of the circuit board with a simple display and clickable button controls. Show the BYU-Idaho logo as permanent artwork on the blue board area, separate from the program-controlled simulated screen. Focus simulation on buttons, screen, LEDs, and buzzer; state clearly which other hardware features are not simulated. Prefer a modern TUI library such as Textual or Rich when suitable.
- In test mode, use a deterministic headless backend that does not launch a terminal UI, require a display, or block for input. Support `pytest` tests that can set button states and inspect display, LED, and buzzer outputs.
- Make backend selection explicit for tests and predictable for interactive use. Avoid hardware or terminal UI side effects merely from importing `pybadge.py`.
- Keep simulator and hardware behavior aligned for shared functions. Document meaningful limitations where a physical feature cannot be represented faithfully by the simulator.

## Evidence and documentation

- Do not guess hardware pin assignments or capabilities. Verify them from board designs, board code, and the local examples before documenting them.
- Distinguish ESP32 GPIO signal numbers from board connector labels and module package lead numbers. Document mappings for the standard jumper-bridge configuration; note that moving/removing bridges changes routing and may disconnect built-in peripherals. Do not assume software can detect physical bridge changes.
- Keep installation commands and firmware guidance aligned with the supplied eBadge setup documentation, and clearly identify any version-specific assumptions.
- Explain how to initialize and use the board through `pybadge.py` once that library exists; avoid documenting APIs that have not been implemented.
