"""Focused terminal simulator for buttons, display, LEDs, and buzzer."""

import os
import threading

from backends.test_backend import TestBackend


class SimulatorBackend(TestBackend):
    """Interactive terminal model for the controls and outputs students use."""

    def __init__(self):
        super().__init__()
        self._app = None
        self._app_thread = None

    def initialize(self):
        super().initialize()
        try:
            from textual.app import App, ComposeResult
            from textual.containers import Horizontal, Vertical
            from textual.widgets import Button, Static
        except ImportError as error:
            raise RuntimeError(
                "The simulator needs Textual. Install the project with its "
                "computer extras or run mode='test'."
            ) from error

        backend = self

        class BadgeApp(App):
            """Small interactive view of the eBadge board."""

            CSS = """
            Screen { align: center middle; }
            #board { width: 76; height: 29; padding: 1 2; background: #07539b; border: round #56a3e8; }
            #brand { height: 7; content-align: center middle; color: white; }
            #controls { height: 9; align: center middle; }
            #directions { width: 24; height: 9; align: center middle; }
            #actions { width: 14; height: 7; align: center middle; }
            .pad-button { min-width: 8; height: 3; margin: 0 1; }
            #screen { width: 32; height: 11; padding: 1; margin: 0 1; border: heavy #d1d5db; background: black; color: white; overflow: hidden; }
            #outputs { height: 4; content-align: center middle; color: white; }
            #help { height: 2; content-align: center middle; color: #dbeafe; }
            """

            TITLE = "BYU-I eBadge Simulator"
            BINDINGS = [("q", "quit", "Quit")]

            def compose(self) -> ComposeResult:
                with Vertical(id="board"):
                    yield Static(backend._logo_art(), id="brand")
                    with Horizontal(id="controls"):
                        with Vertical(id="directions"):
                            yield Button("Up", id="button-up", classes="pad-button")
                            with Horizontal():
                                yield Button("Left", id="button-left", classes="pad-button")
                                yield Button("Down", id="button-down", classes="pad-button")
                                yield Button("Right", id="button-right", classes="pad-button")
                        yield Static(backend._screen_text(), id="screen")
                        with Vertical(id="actions"):
                            yield Button("A", id="button-a", classes="pad-button success")
                            yield Button("B", id="button-b", classes="pad-button warning")
                    yield Static(backend._output_text(), id="outputs")
                    yield Static("Click a button · q quits", id="help")

            def on_button_pressed(self, event: Button.Pressed) -> None:
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
                self.query_one("#screen", Static).update(backend._screen_text())
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
        lines = ["eBadge display 320 x 240"]
        if self.display_operations:
            for operation in self.display_operations[-5:]:
                if operation[0] == "clear":
                    lines.append("[clear {}]".format(operation[1]))
                elif operation[0] == "text":
                    _kind, text, x, y, _color = operation
                    lines.append("{:>3},{:<3} {}".format(x, y, text))
                elif operation[0] == "image":
                    lines.append("[image: {}]".format(operation[1]))
        else:
            lines.append("Your program's screen output")
        return "\n".join(lines)

    def _output_text(self):
        strip_on = sum(1 for color in self.led_strip if color != "off")
        if self.active_tone is None:
            tone = "buzzer: off"
        else:
            tone = "buzzer: {} Hz".format(self.active_tone[0])
        return "RGB LED: {}   Strip LEDs on: {}/24   {}".format(
            self.rgb_led, strip_on, tone
        )

    def joystick(self):
        raise NotImplementedError("joystick movement is not modeled by the terminal simulator")

    def scan_wifi(self, include_details=False):
        raise NotImplementedError("Wi-Fi scanning is not modeled by the terminal simulator")

    def read_accelerometer(self):
        raise NotImplementedError("accelerometer readings are not modeled by the terminal simulator")

    def read_battery_voltage(self):
        raise NotImplementedError("battery voltage is not modeled by the terminal simulator")

    def read_voltage(self, pin):
        raise NotImplementedError("analog voltage is not modeled by the terminal simulator")

    def set_pwm(self, pin, frequency_hz, duty_percent):
        raise NotImplementedError("external GPIO PWM is not modeled by the terminal simulator")


def _composite(rgba, background):
    red, green, blue, alpha = rgba
    amount = alpha / 255.0
    return (
        int(red * amount + background[0] * (1.0 - amount)),
        int(green * amount + background[1] * (1.0 - amount)),
        int(blue * amount + background[2] * (1.0 - amount)),
    )
