"""Display the BYU-Idaho CSE logo prepared from the repository PNG.

Run `python resize_image.py byui-cse.png` from the repository root first. Then
run this example after `pybadge.py` is implemented and the BMP is copied to the
badge when using hardware mode.
"""

import pybadge


def main():
    pybadge.initialize()
    pybadge.display_clear()
    pybadge.display_image("byui-cse_badge.bmp", x=0, y=0)


if __name__ == "__main__":
    main()
