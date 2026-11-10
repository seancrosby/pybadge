"""Play one short tone each time button A is pressed.

Run from the repository root after `pybadge.py` is implemented.
"""

import pybadge


def main():
    pybadge.initialize()
    pybadge.display_clear()
    pybadge.display_text("Press A to play a note", x=8, y=8)
    was_pressed = False

    try:
        while True:
            is_pressed = pybadge.is_pressed(pybadge.BUTTON_A)
            if is_pressed and not was_pressed:
                pybadge.play_tone(440, 180)
            was_pressed = is_pressed
            pybadge.pause(20)
    except KeyboardInterrupt:
        pybadge.stop_tone()


if __name__ == "__main__":
    main()
