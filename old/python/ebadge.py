"""Friendly Python interface to the BYU-Idaho eBadge v4 hardware.

Example::

    import ebadge
    ebadge.display_text("Hello, badge!")
    ebadge.set_led("blue")
    if ebadge.is_pressed(ebadge.button_a):
        ebadge.play_tone(660, 150)

Copy this file and ``board_v4.py`` (plus its display driver and font) to the badge.
"""

import machine
import board_v4 as _board
import os
import utime

# Public color names work with LEDs and the display.
OFF = "off"
RED = "red"
GREEN = "green"
BLUE = "blue"
YELLOW = "yellow"
ORANGE = "orange"
MAGENTA = "magenta"
CYAN = "cyan"
WHITE = "white"
BLACK = "black"
PURPLE = "purple"

_COLORS = {
    BLACK: 0x0000, WHITE: 0xFFFF, RED: 0xF800, GREEN: 0x07E0,
    BLUE: 0x001F, YELLOW: 0xFFE0, ORANGE: 0xFC00,
    MAGENTA: 0xF81F, CYAN: 0x07FF, PURPLE: 0x8010,
}


def _screen_color(color):
    """Convert a friendly color name to the display driver's color value."""
    if isinstance(color, str):
        return _COLORS.get(color.lower(), _COLORS[BLACK])
    return color


class Button:
    """A physical eBadge button that can be checked with :func:`is_pressed`."""
    def __init__(self, name, pin):
        self.name = name
        self._pin = pin

    def __repr__(self):
        return "Button(%r)" % self.name


button_a = Button("A", _board.button_A)
button_b = Button("B", _board.button_B)
button_up = Button("up", _board.button_up)
button_down = Button("down", _board.button_down)
button_left = Button("left", _board.button_left)
button_right = Button("right", _board.button_right)


def initialize(show_status=False):
    """Initialize the LCD and clear it.

    Args:
        show_status: Show the live button and joystick strip at the bottom.
    """
    _board.tft_init(include_status_bar=show_status)


def is_pressed(button):
    """Return ``True`` while one of the public button objects is held down."""
    if not isinstance(button, Button):
        raise TypeError("button must be an ebadge button, such as button_a")
    return _board.is_pressed(button._pin)


def joystick():
    """Return the joystick's raw ``(x, y)`` readings."""
    return _board.joy_read()


def set_led(color):
    """Set the small RGB LED to a color name or an ``(red, green, blue)`` tuple."""
    _board.set_rgb_color(color)


def turn_led_off():
    """Turn off the small RGB LED."""
    _board.rgb_off()


def play_tone(frequency, duration_ms):
    """Play a buzzer tone at ``frequency`` Hz for ``duration_ms`` milliseconds."""
    _board.play_tone(frequency, duration_ms)


def pause(milliseconds):
    """Pause for the given number of milliseconds."""
    _board.sleep(milliseconds)


def set_pixel(index, color):
    """Set one of the 24 ring LEDs by index and color name or RGB tuple."""
    _board.px(index, color)
    _board.addr_show()


def clear_pixels():
    """Turn off all LEDs in the addressable ring."""
    _board.addr_clear()


def display_clear(color=BLACK):
    """Fill the whole LCD with a color (black by default)."""
    _board.tft.fill(_screen_color(color))


def display_text(text, x=8, y=8, color=WHITE):
    """Draw text at pixel position ``(x, y)`` using a friendly color name."""
    _board.tft.text(_board.font, str(text), int(x), int(y), _screen_color(color), _COLORS[BLACK])


def draw_pixel(x, y, color=WHITE):
    """Draw one LCD pixel at ``(x, y)``."""
    _board.tft.pixel(int(x), int(y), _screen_color(color))


def draw_line(x1, y1, x2, y2, color=WHITE):
    """Draw a line between two LCD coordinates."""
    _board.tft.line(int(x1), int(y1), int(x2), int(y2), _screen_color(color))


def draw_rectangle(x, y, width, height, color=WHITE, filled=False):
    """Draw an LCD rectangle; set ``filled=True`` to fill its interior."""
    draw = _board.tft.fill_rect if filled else _board.tft.rect
    draw(int(x), int(y), int(width), int(height), _screen_color(color))


def read_battery():
    """Return the raw battery sensor reading (ADC count, not a percentage)."""
    global _battery_adc
    if _battery_adc is None:
        _battery_adc = machine.ADC(machine.Pin(12))
        try:
            _battery_adc.atten(machine.ADC.ATTN_11DB)
        except AttributeError:
            pass
    return _battery_adc.read()


def read_accelerometer():
    """Return acceleration as ``(x, y, z)`` in g, or ``None`` if unavailable."""
    global _accel_bus, _accel_checked
    if not _accel_checked:
        _accel_checked = True
        try:
            bus = machine.I2C(0, scl=machine.Pin(42), sda=machine.Pin(41), freq=400000)
            if 0x1C not in bus.scan() or bus.readfrom_mem(0x1C, 0x0D, 1)[0] not in (0x1A, 0x2A):
                return None
            bus.writeto_mem(0x1C, 0x0E, b"\x00")
            bus.writeto_mem(0x1C, 0x2A, b"\x01")
            _accel_bus = bus
        except OSError:
            return None
    if _accel_bus is None:
        return None
    try:
        data = _accel_bus.readfrom_mem(0x1C, 0x01, 6)
    except OSError:
        return None
    values = []
    for i in (0, 2, 4):
        raw = ((data[i] << 8) | data[i + 1]) >> 2
        if raw > 8191:
            raw -= 16384
        values.append(raw / 1024.0)
    return tuple(values)


def connect_wifi(name, password, timeout_ms=15000):
    """Connect to a Wi-Fi network; return ``True`` on success, else ``False``.

    Args:
        name: Wi-Fi network name (SSID).
        password: Network password, or an empty string for an open network.
        timeout_ms: Maximum time to wait for a connection.
    """
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(name, password)
        start = utime.ticks_ms()
        while not wlan.isconnected() and utime.ticks_diff(utime.ticks_ms(), start) < timeout_ms:
            utime.sleep_ms(100)
    return wlan.isconnected()


def disconnect_wifi():
    """Disconnect from Wi-Fi and turn off the station interface."""
    import network
    wlan = network.WLAN(network.STA_IF)
    if wlan.active():
        wlan.disconnect()
        wlan.active(False)


def download_url(url, filename=None):
    """Download a URL and return its bytes, or save them and return the filename.

    Requires the optional ``urequests`` module on the badge. Use HTTPS URLs for
    encrypted downloads. Large files should be saved directly to a file when
    memory is limited.
    """
    try:
        import urequests as requests
    except ImportError:
        import requests
    response = requests.get(url)
    try:
        if response.status_code < 200 or response.status_code >= 300:
            raise OSError("HTTP status %d" % response.status_code)
        content = response.content
        if filename is None:
            return content
        with open(filename, "wb") as output:
            output.write(content)
        return filename
    finally:
        response.close()


def start_bluetooth():
    """Turn on Bluetooth Low Energy and return the BLE radio object.

    Raises ``ImportError`` if the installed firmware has no Bluetooth support.
    """
    import bluetooth
    global _ble, _bluetooth_module
    _bluetooth_module = bluetooth
    _ble = bluetooth.BLE()
    _ble.active(True)
    return _ble


def scan_bluetooth(duration_ms=4000):
    """Scan for nearby Bluetooth LE advertisers.

    Return ``(address, address_type, signal_strength)`` tuples. ``address`` is
    a colon-separated hexadecimal string. Scanning is passive and does not pair.
    """
    ble = _ble if _ble is not None else start_bluetooth()
    seen = {}
    module = _bluetooth_module

    def receive(event, data):
        if event == module._IRQ_SCAN_RESULT:
            try:
                addr_type, address, _adv_type, rssi, _payload = data
                key = bytes(address)
                if key not in seen or rssi > seen[key][0]:
                    seen[key] = (rssi, addr_type)
            except (TypeError, ValueError):
                pass

    ble.irq(receive)
    ble.gap_scan(duration_ms, 30000, 30000, False)
    utime.sleep_ms(duration_ms + 100)
    try:
        ble.gap_scan(None)
    except Exception:
        pass
    results = []
    for address, details in seen.items():
        rssi, addr_type = details
        results.append((":".join("%02x" % byte for byte in address), addr_type, rssi))
    return results


def stop_bluetooth():
    """Turn off the Bluetooth LE radio if it has been started."""
    if _ble is not None:
        _ble.active(False)


def connect_bluetooth(address, address_type=0, timeout_ms=10000):
    """Connect to a nearby BLE device and return its connection handle.

    ``address`` is a six-byte colon-separated address returned by
    :func:`scan_bluetooth`; use the accompanying address type. Returns ``None``
    if no connection is made in time.
    BLE devices may require additional GATT service discovery after connecting.
    """
    if isinstance(address, tuple):
        address, address_type = address[0], address[1]
    ble = _ble if _ble is not None else start_bluetooth()
    module = _bluetooth_module
    if isinstance(address, str):
        address_bytes = bytes(int(part, 16) for part in address.split(":"))
    else:
        address_bytes = bytes(address)
    result = {"handle": None}

    def receive(event, data):
        if event == module._IRQ_PERIPHERAL_CONNECT:
            result["handle"] = data[0]

    ble.irq(receive)
    ble.gap_connect(int(address_type), address_bytes)
    start = utime.ticks_ms()
    while result["handle"] is None and utime.ticks_diff(utime.ticks_ms(), start) < timeout_ms:
        utime.sleep_ms(50)
    return result["handle"]


def configure_pin(number, mode="input", pull=None):
    """Configure an external GPIO pin numbered 13 through 18 as input or output.

    ``pull`` may be ``"up"``, ``"down"``, or ``None``. Use only the badge's
    exposed breadboard pins, and never connect a pin to a voltage above 3.3 V.
    """
    number = int(number)
    if number not in (13, 14, 15, 16, 17, 18):
        raise ValueError("external pin must be GPIO 13 through 18")
    mode = mode.lower()
    if mode not in ("input", "output"):
        raise ValueError("mode must be 'input' or 'output'")
    if pull not in (None, "up", "down"):
        raise ValueError("pull must be None, 'up', or 'down'")
    pin_mode = machine.Pin.IN if mode == "input" else machine.Pin.OUT
    if pull is None:
        pin = machine.Pin(number, pin_mode)
    else:
        pull_mode = machine.Pin.PULL_UP if pull == "up" else machine.Pin.PULL_DOWN
        pin = machine.Pin(number, pin_mode, pull=pull_mode)
    _pins[number] = pin
    return pin


def read_pin(number):
    """Read and return the current 0 or 1 value of a configured GPIO pin."""
    pin = _pins.get(int(number))
    if pin is None:
        raise ValueError("configure the pin before reading it")
    return pin.value()


def write_pin(number, value):
    """Set a configured output pin to 0/False (low) or 1/True (high)."""
    pin = _pins.get(int(number))
    if pin is None:
        raise ValueError("configure the pin before writing it")
    pin.value(1 if value else 0)


def initialize_sd_card(sck, mosi, miso, chip_select, mount_point="/sd"):
    """Initialize and mount the SD slot using SPI and the supplied GPIO numbers.

    GPIO mapping depends on the specific badge revision. The caller must supply
    the slot's actual clock, MOSI, MISO, and chip-select wiring.
    """
    global _sd_card, _sd_mount_point
    try:
        import vfs
    except ImportError:
        vfs = os
    sd_type = machine.SDCard
    try:
        _sd_card = sd_type(slot=2, sck=machine.Pin(sck), mosi=machine.Pin(mosi),
                           miso=machine.Pin(miso), cs=machine.Pin(chip_select))
    except TypeError:
        _sd_card = sd_type(slot=2, sck=sck, mosi=mosi, miso=miso, cs=chip_select)
    _sd_mount_point = mount_point
    vfs.mount(_sd_card, mount_point)
    return True


def sd_card_present(sck=None, mosi=None, miso=None, chip_select=None, mount_point="/sd"):
    """Return whether an SD card can be mounted, optionally initializing it first.

    Pass the slot's GPIO mapping on the first call. A mounted card is reused.
    """
    global _sd_card
    if _sd_card is not None:
        try:
            os.listdir(_sd_mount_point)
            return True
        except OSError:
            return False
    if None in (sck, mosi, miso, chip_select):
        return False
    try:
        initialize_sd_card(sck, mosi, miso, chip_select, mount_point)
        return True
    except OSError:
        _sd_card = None
        return False


def list_files(path="/sd"):
    """Return the names of files and folders in a directory."""
    return os.listdir(path)


def read_file(path):
    """Read a text file and return its contents as a string."""
    with open(path, "r") as source:
        return source.read()


def write_file(path, contents):
    """Write text to a file, replacing its previous contents."""
    with open(path, "w") as destination:
        destination.write(contents)


def read_bytes(path):
    """Read a file as bytes, useful for images and other binary data."""
    with open(path, "rb") as source:
        return source.read()


def write_bytes(path, contents):
    """Write bytes to a file, replacing its previous contents."""
    with open(path, "wb") as destination:
        destination.write(contents)


def unmount_sd_card(mount_point=None):
    """Unmount the mounted SD card."""
    global _sd_card, _sd_mount_point
    point = mount_point or _sd_mount_point
    if point is None:
        return
    try:
        os.umount(point)
    except OSError:
        pass
    _sd_card = None
    _sd_mount_point = None


def display_image(path, x=0, y=0, max_width=320, max_height=240):
    """Display an uncompressed 24-bit BMP image, shrinking it to fit the bounds.

    The image is scaled proportionally with nearest-neighbor sampling. BMP files
    should be uncompressed (BI_RGB); PNG and JPEG are not supported by this
    lightweight MicroPython helper.
    """
    with open(path, "rb") as image_file:
        header = image_file.read(54)
        if len(header) < 54 or header[:2] != b"BM":
            raise ValueError("image must be a BMP file")
        pixel_offset = int.from_bytes(header[10:14], "little")
        width = int.from_bytes(header[18:22], "little", signed=True)
        signed_height = int.from_bytes(header[22:26], "little", signed=True)
        bits = int.from_bytes(header[28:30], "little")
        compression = int.from_bytes(header[30:34], "little")
        if width <= 0 or signed_height == 0 or bits != 24 or compression != 0:
            raise ValueError("only uncompressed 24-bit BMP images are supported")
        height = abs(signed_height)
        top_down = signed_height < 0
        if max_width <= 0 or max_height <= 0:
            raise ValueError("maximum image dimensions must be positive")
        scale = min(1.0, max_width / width, max_height / height)
        out_width = max(1, int(width * scale))
        out_height = max(1, int(height * scale))
        row_bytes = ((width * 3 + 3) // 4) * 4
        for out_y in range(out_height):
            source_y = int(out_y / scale)
            bmp_y = source_y if top_down else height - 1 - source_y
            image_file.seek(pixel_offset + bmp_y * row_bytes)
            row = image_file.read(row_bytes)
            pixels = bytearray(out_width * 2)
            for out_x in range(out_width):
                source_x = int(out_x / scale)
                offset = source_x * 3
                blue, green, red = row[offset], row[offset + 1], row[offset + 2]
                color = ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)
                byte_index = out_x * 2
                if _board.tft.needs_swap:
                    pixels[byte_index] = color & 0xFF
                    pixels[byte_index + 1] = color >> 8
                else:
                    pixels[byte_index] = color >> 8
                    pixels[byte_index + 1] = color & 0xFF
            _board.tft.blit_buffer(pixels, int(x), int(y) + out_y, out_width, 1)


_battery_adc = None
_accel_bus = None
_accel_checked = False
_ble = None
_bluetooth_module = None
_pins = {}
_sd_card = None
_sd_mount_point = None
