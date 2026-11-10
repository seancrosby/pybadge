# Project instructions

## Project purpose

This repository develops a beginner-friendly MicroPython interface for the BYU-Idaho eBadge. The main library will be `pybadge.py`. Its public helpers should let students who know Python functions work with the board without needing to understand low-level electronics or C-style hardware APIs.

## Intended repository structure

- `pybadge.py`: the student-facing helper library for supported eBadge functions.
- A hardware backend for running `pybadge.py` on the physical eBadge and a computer simulator backend for running the same student programs on a regular computer.
- `board/`: board designs and code samples used as source material for hardware details. Keep the e-badge source repository here as a Git submodule; the project is currently targeting board version V4.1.1.
- `specifications/`: software and board specifications. Include Python coding standards and a board specification describing physical layout, pins, connected components, and capabilities such as Wi-Fi. Derive board facts from the materials in `board/` and cite or point to the relevant source files where practical.
- `README.md`: explain the repository, its structure, and how to set up and use the board. Embed the repository's `byui-ebadge-4_0.jpg` image. Include the MicroPython installation instructions from `hardware/ebadge/README.md`, adapting paths to the final layout as needed.

## Hardware source and version scope

- The upstream source is `git@github.com:BYU-I-eBadge/e-badge.git`, included as a Git submodule under `board/`.
- The current target is V4.1.1. Its layout is in the upstream repository's `hardware/v4.1.1` directory.
- Consult other upstream component information as needed. Use the examples under `hardware/ebadge/python-files` in this repository to identify component-to-pin mappings and demonstrated capabilities.
- The board specification must explain the visual layout of the eBadge: button locations, screen location, and empty/exposed headers. Use the board design materials and `byui-ebadge-4_0.jpg` as evidence. Distinguish confirmed facts from anything that remains uncertain.
- Preserve the existing `hardware/ebadge` materials as reference/course examples unless a task explicitly asks to change them.

## Python standards and examples

- Define practical Python best practices in `specifications/` for new project code, especially `pybadge.py`: readable names, small focused functions, useful docstrings, clear errors, and MicroPython compatibility.
- Apply those standards to newly developed project code. Files in `board/` are upstream designs and samples and are examples only; do not reformat or otherwise impose project Python standards on them.
- Keep the student-facing API approachable and hide pin-level details when a simple helper can safely express the action.

## Cross-platform runtime and simulator

- `pybadge.py` must work both on the physical eBadge and on a regular computer. Keep the student-facing API consistent across both environments so example programs do not need hardware-specific changes.
- On the eBadge, `pybadge.py` must delegate hardware operations to an underlying library that interfaces with the board. On a computer, it must delegate to an underlying simulator rather than attempting to import or access hardware-only APIs.
- The interactive computer simulator should provide a terminal-based visual of the eBadge circuit board, including a simple display and clickable controls for buttons. Prefer a modern terminal UI library such as Textual or Rich when suitable; keep simulator behavior understandable and usable for learners.
- Programs using `pybadge.py` must be unit-testable with `pytest`. Support a headless computer mode that does not launch a terminal UI, require a display, or block tests for input. Provide deterministic simulator state and a way for tests to control inputs and inspect outputs through the public interface or test fixtures.
- Avoid hardware or terminal UI side effects merely from importing `pybadge.py`. Initialize the appropriate backend deliberately, and make it possible to select or inject a backend in tests without changing student program code.
- Keep simulator and hardware behavior aligned for shared functions. Document meaningful limitations where a physical feature cannot be represented faithfully by the simulator.

## Evidence and documentation

- Do not guess hardware pin assignments or capabilities. Verify them from board designs, board code, and the local examples before documenting them.
- Keep installation commands and firmware guidance aligned with the supplied eBadge setup documentation, and clearly identify any version-specific assumptions.
- Explain how to initialize and use the board through `pybadge.py` once that library exists; avoid documenting APIs that have not been implemented.
