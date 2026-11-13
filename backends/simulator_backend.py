"""Focused terminal simulator for buttons, display, LEDs, and buzzer."""

import os
import threading
import time

from backends.test_backend import TestBackend
from pybadge import UnsupportedFeatureError


class SimulatorBackend(TestBackend):
    """Interactive terminal model for the board controls and outputs."""

    def __init__(self):
        super().__init__()
        self._app = None
        self._app_thread = None
        self._tone_deadline = None

    def initialize(self):
        super().initialize()
        try:
            from textual.app import App, ComposeResult
            from textual.containers import Horizontal, Vertical
            from textual.widgets import Button, Static
        except ImportError as error:
            raise RuntimeError(
                "The simulator needs Textual. Install it with "
                "'python -m pip install textual' or run mode='test'."
            ) from error

        backend = self

        class BadgeApp(App):
            """Small interactive view of the eBadge board."""

            CSS = """
            Screen { align: center middle; }
            #board { width: 94; height: 35; padding: 1 2; background: #07539b; border: round #56a3e8; }
            #brand { height: 7; content-align: center middle; color: white; }
            #controls { height: 15; align: center middle; }
            #buttons { width: 26; height: 14; align: center middle; }
            #directions { height: 9; align: center middle; }
            #actions { height: 3; align: center middle; }
            #screen { width: 34; height: 13; padding: 1; margin: 0 1; border: heavy #d1d5db; background: black; color: white; overflow: hidden; }
            #joystick { width: 23; height: 13; align: center middle; }
            .joystick-row { height: 3; align: center middle; }
            #stick-label { height: 1; content-align: center middle; color: #dbeafe; }
            .pad-button { min-width: 6; height: 3; margin: 0 1; }
            .stick-button { min-width: 5; height: 3; margin: 0 0; }
            #stick-center { min-width: 9; }
            #outputs { height: 6; content-align: center middle; color: white; }
            #help { height: 2; content-align: center middle; color: #dbeafe; }
            """

            TITLE = "BYU-I eBadge Simulator"
            BINDINGS = [("q", "quit", "Quit")]

            def compose(self) -> ComposeResult:
                with Vertical(id="board"):
                    yield Static(backend._logo_art(), id="brand")
                    with Horizontal(id="controls"):
                        with Vertical(id="buttons"):
                            with Vertical(id="directions"):
                                yield Button("Up", id="button-up", classes="pad-button")
                                with Horizontal():
                                    yield Button("Left", id="button-left", classes="pad-button")
                                    yield Button("Down", id="button-down", classes="pad-button")
                                    yield Button("Right", id="button-right", classes="pad-button")
                            with Horizontal(id="actions"):
                                yield Button("A", id="button-a", classes="pad-button success")
                                yield Button("B", id="button-b", classes="pad-button warning")
                        yield Static(backend._screen_text(), id="screen")
                        with Vertical(id="joystick"):
                            yield Static("Joystick", id="stick-label")
                            with Horizontal(classes="joystick-row"):
                                yield Button("NW", id="stick-nw", classes="stick-button")
                                yield Button("N", id="stick-n", classes="stick-button")
                                yield Button("NE", id="stick-ne", classes="stick-button")
                            with Horizontal(classes="joystick-row"):
                                yield Button("W", id="stick-w", classes="stick-button")
                                yield Button("Center", id="stick-center", classes="stick-button")
                                yield Button("E", id="stick-e", classes="stick-button")
                            with Horizontal(classes="joystick-row"):
                                yield Button("SW", id="stick-sw", classes="stick-button")
                                yield Button("S", id="stick-s", classes="stick-button")
                                yield Button("SE", id="stick-se", classes="stick-button")
                    yield Static(backend._output_text(), id="outputs")
                    yield Static(
                        "Click controls · center the stick to reset · q closes the board",
                        id="help",
                    )

            def on_button_pressed(self, event: Button.Pressed) -> None:
                stick_values = {
                    "stick-nw": (-1.0, 1.0),
                    "stick-n": (0.0, 1.0),
                    "stick-ne": (1.0, 1.0),
                    "stick-w": (-1.0, 0.0),
                    "stick-center": (0.0, 0.0),
                    "stick-e": (1.0, 0.0),
                    "stick-sw": (-1.0, -1.0),
                    "stick-s": (0.0, -1.0),
                    "stick-se": (1.0, -1.0),
                }
                stick = stick_values.get(event.button.id)
                if stick is not None:
                    backend.set_joystick(*stick)
                    return

                button = {
                    "button-a": "A",
                    "button-b": "B",
                    "button-up": "up",
                    "button-down": "down",
                    "button-left": "left",
                    "button-right": "right",
                }.get(event.button.id)
                if button is None:
                    return
                backend.press_button(button)
                self.set_timer(0.18, lambda: backend.release_button(button))

            def on_mount(self) -> None:
                self.set_interval(0.1, self.refresh_board)

            def refresh_board(self) -> None:
                screen = self.query_one("#screen", Static)
                screen.styles.background = _color_style(backend.display_color)
                screen.update(backend._screen_text())
                self.query_one("#outputs", Static).update(backend._output_text())

        self._app = BadgeApp()
        self._app_thread = threading.Thread(
            target=self._app.run,
            name="pybadge-terminal-simulator",
            daemon=True,
        )
        self._app_thread.start()

    def shutdown(self):
        if self._app is not None:
            try:
                self._app.exit()
            except Exception:
                pass
        self._app = None
        self._app_thread = None
        super().shutdown()
        self._tone_deadline = None

    def _logo_art(self):
        """Render the CSE logo as permanent blue-board artwork in true color."""
        try:
            from PIL import Image
            from rich.text import Text

            logo_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "byui-cse.png"
            )
            with Image.open(logo_path) as image:
                image = image.convert("RGBA")
                image.thumbnail((28, 10))
                width, height = image.size
                pixels = image.load()
                art = Text()
                for y in range(0, height, 2):
                    for x in range(width):
                        top = _composite(pixels[x, y], (7, 83, 155))
                        if y + 1 < height:
                            bottom = _composite(pixels[x, y + 1], (7, 83, 155))
                        else:
                            bottom = (7, 83, 155)
                        top_hex = "#%02x%02x%02x" % top
                        bottom_hex = "#%02x%02x%02x" % bottom
                        art.append("▀", style="{} on {}".format(top_hex, bottom_hex))
                    art.append("\n")
                return art
        except Exception:
            # The board label stays visible if terminal true-color art is not
            # available, for example on a restricted terminal emulator.
            return "BYU-IDAHO  ·  COMPUTER SCIENCE"

    def _screen_text(self):
        from rich.text import Text

        screen = Text()
        screen.append("eBadge display 320 x 240\n", style="bold")
        if self.display_operations:
            for operation in self.display_operations[-5:]:
                if operation[0] == "clear":
                    screen.append(
                        "[clear {}]\n".format(operation[1]),
                        style=_color_style(operation[1]),
                    )
                elif operation[0] == "text":
                    _kind, text, x, y, color = operation
                    screen.append(
                        "{:>3},{:<3} {}\n".format(x, y, text),
                        style=_color_style(color),
                    )
                elif operation[0] == "pixel":
                    _kind, x, y, color = operation
                    screen.append(
                        "pixel {},{}\n".format(x, y), style=_color_style(color)
                    )
                elif operation[0] == "line":
                    _kind, x1, y1, x2, y2, color = operation
                    screen.append(
                        "line {},{} to {},{}\n".format(x1, y1, x2, y2),
                        style=_color_style(color),
                    )
                elif operation[0] == "rectangle":
                    _kind, x, y, width, height, color, filled = operation
                    shape = "filled rectangle" if filled else "rectangle"
                    screen.append(
                        "{} {},{} {}x{}\n".format(shape, x, y, width, height),
                        style=_color_style(color),
                    )
                elif operation[0] == "image":
                    screen.append("[image: {}]\n".format(operation[1]))
        else:
            screen.append("Your program's screen output")
        return screen

    def _output_text(self):
        from rich.text import Text

        if (
            self.active_tone is not None
            and self._tone_deadline is not None
            and time.monotonic() >= self._tone_deadline
        ):
            self.active_tone = None
            self._tone_deadline = None

        output = Text("RGB ")
        output.append("●", style="bold {}".format(_color_style(self.rgb_led)))
        output.append(" {}   Ring ".format(self.rgb_led))
        for color in self.led_strip:
            output.append("●", style="bold {}".format(_color_style(color)))
        if self.active_tone is None:
            tone = "buzzer off"
        else:
            tone = "buzzer {} Hz".format(self.active_tone[0])
        output.append("   {}".format(tone))
        output.append(
            "\nJoystick: ({:.1f}, {:.1f})".format(*self.joystick_values)
        )
        return output

    def joystick(self):
        return self.joystick_values

    def play_tone(self, frequency_hz, duration_ms):
        super().play_tone(frequency_hz, duration_ms)
        self._tone_deadline = time.monotonic() + duration_ms / 1000.0

    def stop_tone(self):
        super().stop_tone()
        self._tone_deadline = None

    def pause(self, milliseconds):
        time.sleep(milliseconds / 1000.0)

    def display_clear(self, color):
        super().display_clear(color)
        self.display_operations = [("clear", color)]

    def display_text(self, text, x, y, color):
        super().display_text(text, x, y, color)
        self._trim_display_history()

    def draw_pixel(self, x, y, color):
        super().draw_pixel(x, y, color)
        self._trim_display_history()

    def draw_line(self, x1, y1, x2, y2, color):
        super().draw_line(x1, y1, x2, y2, color)
        self._trim_display_history()

    def draw_rectangle(self, x, y, width, height, color, filled):
        super().draw_rectangle(x, y, width, height, color, filled)
        self._trim_display_history()

    def display_image(self, path, x, y):
        super().display_image(path, x, y)
        self._trim_display_history()

    def _trim_display_history(self):
        if len(self.display_operations) > 20:
            self.display_operations = self.display_operations[-20:]

    def scan_wifi(self, include_details=False):
        raise UnsupportedFeatureError(
            "Wi-Fi scanning is not modeled by the terminal simulator."
        )

    def read_accelerometer(self):
        raise UnsupportedFeatureError(
            "Accelerometer readings are not modeled by the terminal simulator."
        )

    def read_battery_voltage(self):
        raise UnsupportedFeatureError(
            "Battery voltage is not modeled by the terminal simulator."
        )

    def read_voltage(self, pin):
        raise UnsupportedFeatureError(
            "External analog voltage is not modeled by the terminal simulator."
        )

    def set_pwm(self, pin, frequency_hz, duty_percent):
        raise UnsupportedFeatureError(
            "External GPIO PWM is not modeled by the terminal simulator."
        )

    def configure_pin(self, pin, mode, pull):
        raise UnsupportedFeatureError(
            "External GPIO configuration is not modeled by the terminal simulator."
        )

    def read_pin(self, pin):
        raise UnsupportedFeatureError(
            "External GPIO reads are not modeled by the terminal simulator."
        )

    def write_pin(self, pin, value):
        raise UnsupportedFeatureError(
            "External GPIO writes are not modeled by the terminal simulator."
        )

    def stop_pwm(self, pin):
        raise UnsupportedFeatureError(
            "External GPIO PWM is not modeled by the terminal simulator."
        )


def _color_style(color):
    if isinstance(color, (tuple, list)):
        red, green, blue = color
        return "#%02x%02x%02x" % (red, green, blue)
    colors = {
        "off": "#49627a",
        "black": "#000000",
        "white": "#ffffff",
        "red": "#ff0000",
        "green": "#00ff00",
        "blue": "#0000ff",
        "yellow": "#ffff00",
        "orange": "#ff8000",
        "magenta": "#ff00ff",
        "cyan": "#00ffff",
        "purple": "#800080",
    }
    return colors.get(color, "#ffffff")


def _composite(rgba, background):
    red, green, blue, alpha = rgba
    amount = alpha / 255.0
    return (
        int(red * amount + background[0] * (1.0 - amount)),
        int(green * amount + background[1] * (1.0 - amount)),
        int(blue * amount + background[2] * (1.0 - amount)),
    )
