"""Light the RGB LED while button A is held.

Run from the repository root after `pybadge.py` is implemented.
"""

import pybadge


def main():
    pybadge.initialize()
    print("Hold button A to light the LED. Press Ctrl-C to stop.")

    try:
        while True:
            if pybadge.is_pressed(pybadge.BUTTON_A):
                pybadge.set_rgb_led("blue")
            else:
                pybadge.turn_rgb_led_off()
            pybadge.pause(20)
    except KeyboardInterrupt:
        pybadge.turn_rgb_led_off()


if __name__ == "__main__":
    main()
