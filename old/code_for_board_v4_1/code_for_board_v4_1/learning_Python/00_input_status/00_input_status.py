# Lesson 00 — Live inputs: buttons, joystick, accelerometer, battery (B = menu).
#
# Labels are drawn once; only value areas are erased and redrawn when that reading
# changes (less flicker). Accelerometer is the MMA8452 on I2C (v4: SDA 41, SCL 42).
# Battery is raw ADC on GPIO 12 (same as demo firmware); not the same as “percent charged.”

import machine

from board_v4 import *

# v4 hardware (see demo-programs-arduino.ino)
PIN_I2C_SDA = 41
PIN_I2C_SCL = 42
ACCEL_I2C_ADDR = 0x1C
WHO_MMA8451 = 0x1A
WHO_MMA8452 = 0x2A
PIN_BATTERY_ADC = 12

tft_init(include_status_bar=False)

draw_console_line_at_row(0, "00 — Input status", st7789.CYAN)
draw_console_line_at_row(1, "Press B to return to menu", st7789.YELLOW)

_fw = getattr(font, "WIDTH", 8)

_i2c = None
_accel_ok = False
_bat_adc = None


def _row_y(row):
    return MARGIN_Y + int(row) * LINE_PX


def _paint_value_slot(x, y, text, fg):
    """Clear a slot wide enough for `text` and draw it (does not touch pixels outside the slot)."""
    w = len(text) * _fw
    tft.fill_rect(x, y, w, LINE_PX, st7789.BLACK)
    tft.text(font, text, x, y, fg, st7789.BLACK)


def _try_init_accel():
    """Wake MMA8451/8452 if present; return True when reads should work."""
    global _i2c, _accel_ok
    try:
        bus = machine.I2C(
            0,
            scl=machine.Pin(PIN_I2C_SCL),
            sda=machine.Pin(PIN_I2C_SDA),
            freq=400000,
        )
        if ACCEL_I2C_ADDR not in bus.scan():
            _i2c = None
            _accel_ok = False
            return False
        who = bus.readfrom_mem(ACCEL_I2C_ADDR, 0x0D, 1)[0]
        if who not in (WHO_MMA8451, WHO_MMA8452):
            _i2c = None
            _accel_ok = False
            return False
        # ±2g range, then active mode (CTRL_REG1 = 0x2A).
        bus.writeto_mem(ACCEL_I2C_ADDR, 0x0E, b"\x00")
        bus.writeto_mem(ACCEL_I2C_ADDR, 0x2A, b"\x01")
        _i2c = bus
        _accel_ok = True
        return True
    except OSError:
        _i2c = None
        _accel_ok = False
        return False


def _read_accel_g():
    """Return (ax, ay, az) in g, or (0, 0, 0) if unavailable."""

    def _pair_to_g(msb, lsb):
        raw14 = ((msb << 8) | lsb) >> 2
        if raw14 > 8191:
            raw14 -= 16384
        # ±2g mode: ~1024 LSB per g on MMA8452.
        return raw14 / 1024.0

    if not _accel_ok or _i2c is None:
        return 0.0, 0.0, 0.0
    try:
        d = _i2c.readfrom_mem(ACCEL_I2C_ADDR, 0x01, 6)
        return _pair_to_g(d[0], d[1]), _pair_to_g(d[2], d[3]), _pair_to_g(d[4], d[5])
    except OSError:
        return 0.0, 0.0, 0.0


def _read_battery_raw():
    """Raw ADC count (ESP32-S3 is typically 0–4095 with 12-bit)."""
    global _bat_adc
    if _bat_adc is None:
        _bat_adc = machine.ADC(machine.Pin(PIN_BATTERY_ADC))
        try:
            _bat_adc.atten(machine.ADC.ATTN_11DB)
        except AttributeError:
            pass
    return _bat_adc.read()


def _paint_button_labels_and_slots():
    y = _row_y(2)
    x = MARGIN_X
    xs = []
    for lab in ("A:", "B:", "U:", "D:", "L:", "R:"):
        tft.text(font, lab, x, y, st7789.WHITE, st7789.BLACK)
        x += len(lab) * _fw
        xs.append(x)
        x += _fw
        x += _fw
    return xs


def _paint_joystick_labels_and_slots():
    y = _row_y(3)
    x = MARGIN_X
    s0 = "Joystick  X:"
    tft.text(font, s0, x, y, st7789.GREEN, st7789.BLACK)
    x += len(s0) * _fw
    vx_x = x
    x += 5 * _fw
    s1 = " Y:"
    tft.text(font, s1, x, y, st7789.GREEN, st7789.BLACK)
    x += len(s1) * _fw
    vy_x = x
    return vx_x, vy_x


def _paint_accel_labels_and_slots():
    y = _row_y(4)
    x = MARGIN_X
    xs = []
    for lab in ("Ax:", " Ay:", " Az:"):
        tft.text(font, lab, x, y, st7789.CYAN, st7789.BLACK)
        x += len(lab) * _fw
        xs.append(x)
        x += 5 * _fw
    return xs


def _paint_battery_label_and_slot():
    y = _row_y(5)
    x = MARGIN_X
    s0 = "Batt ADC:"
    tft.text(font, s0, x, y, st7789.YELLOW, st7789.BLACK)
    x += len(s0) * _fw
    return x


_try_init_accel()
_btn_xs = _paint_button_labels_and_slots()
_vx_x, _vy_x = _paint_joystick_labels_and_slots()
_accel_xs = _paint_accel_labels_and_slots()
_bat_x = _paint_battery_label_and_slot()

prev_a = prev_b = prev_u = prev_d = prev_l = prev_r = None
prev_vx = prev_vy = None
prev_ax = prev_ay = prev_az = None
prev_bat = None
_accel_na_painted = False

while True:
    vx, vy = joy_read()
    a = int(is_pressed(button_A))
    b = int(is_pressed(button_B))
    u = int(is_pressed(button_up))
    d = int(is_pressed(button_down))
    l = int(is_pressed(button_left))
    r = int(is_pressed(button_right))

    y2 = _row_y(2)
    if a != prev_a:
        prev_a = a
        _paint_value_slot(_btn_xs[0], y2, str(a), st7789.WHITE)
    if b != prev_b:
        prev_b = b
        _paint_value_slot(_btn_xs[1], y2, str(b), st7789.WHITE)
    if u != prev_u:
        prev_u = u
        _paint_value_slot(_btn_xs[2], y2, str(u), st7789.WHITE)
    if d != prev_d:
        prev_d = d
        _paint_value_slot(_btn_xs[3], y2, str(d), st7789.WHITE)
    if l != prev_l:
        prev_l = l
        _paint_value_slot(_btn_xs[4], y2, str(l), st7789.WHITE)
    if r != prev_r:
        prev_r = r
        _paint_value_slot(_btn_xs[5], y2, str(r), st7789.WHITE)

    y3 = _row_y(3)
    if vx != prev_vx:
        prev_vx = vx
        _paint_value_slot(_vx_x, y3, "%5d" % vx, st7789.GREEN)
    if vy != prev_vy:
        prev_vy = vy
        _paint_value_slot(_vy_x, y3, "%5d" % vy, st7789.GREEN)

    y4 = _row_y(4)
    if not _accel_ok:
        if not _accel_na_painted:
            _accel_na_painted = True
            for i in range(3):
                _paint_value_slot(_accel_xs[i], y4, "  n/a", st7789.CYAN)
    else:
        ax, ay, az = _read_accel_g()
        rx, ry, rz = round(ax, 1), round(ay, 1), round(az, 1)
        if rx != prev_ax:
            prev_ax = rx
            _paint_value_slot(_accel_xs[0], y4, "%5.1f" % ax, st7789.CYAN)
        if ry != prev_ay:
            prev_ay = ry
            _paint_value_slot(_accel_xs[1], y4, "%5.1f" % ay, st7789.CYAN)
        if rz != prev_az:
            prev_az = rz
            _paint_value_slot(_accel_xs[2], y4, "%5.1f" % az, st7789.CYAN)

    y5 = _row_y(5)
    br = _read_battery_raw()
    if br != prev_bat:
        prev_bat = br
        _paint_value_slot(_bat_x, y5, "%5d" % min(br, 99999), st7789.YELLOW)

    if b:
        sleep(120)
        while is_pressed(button_B):
            sleep(20)
        rgb_off()
        break

    sleep(25)
