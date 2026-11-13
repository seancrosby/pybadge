"""Draw basic shapes using the public display helpers."""

import pybadge


def main():
    """Show pixels, lines, and outlined and filled rectangles."""
    pybadge.initialize()
    try:
        pybadge.display_clear(pybadge.BLACK)
        pybadge.display_text("Display shapes", x=8, y=8)
        pybadge.draw_pixel(20, 40, pybadge.RED)
        pybadge.draw_line(35, 40, 110, 40, pybadge.BLUE)
        pybadge.draw_rectangle(20, 60, 90, 50, pybadge.GREEN)
        pybadge.draw_rectangle(130, 60, 90, 50, pybadge.YELLOW, filled=True)
        print("Drawing is complete. Press Ctrl-C to stop.")
        while True:
            pybadge.pause(1000)
    except KeyboardInterrupt:
        pass
    finally:
        pybadge.shutdown()


if __name__ == "__main__":
    main()
