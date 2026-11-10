# Etch-a-Sketch — e-Badge v4 (learning_Python). Port of v3 etch-a-sketch-micropython using board_v4.

import math
import utime

from board_v4 import (
    DISPLAY_W,
    DISPLAY_H,
    tft,
    font,
    st7789,
    tft_init,
    is_pressed,
    button_A,
    button_B,
    button_up,
    button_down,
    button_left,
    button_right,
    joy_read,
    play_tone,
    set_rgb_color,
)

tft_init(include_status_bar=False)

DRAW_AREA_MARGIN = 10
TOP_TEXT_MARGIN = 18

JOYSTICK_CENTER = 2048
JOYSTICK_DEADZONE = 600
JOYSTICK_MAX = 4095

CURSOR_SPEED = 0.3
JOYSTICK_CURVE = 0.5
BUTTON_MOVE_SPEED = 2.0
BUTTON_DEBOUNCE = 200
BUTTON_REPEAT_DELAY = 50

COLORS = [
    st7789.WHITE,
    0x07FF,
    0xFFE0,
    0xF81F,
    0x07E0,
    0xF800,
    0x001F,
    0xFD20,
    0x8410,
    0xFF80,
]
NUM_COLORS = len(COLORS)

RGB_COLORS = [
    (255, 255, 255),
    (0, 255, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 255),
    (255, 165, 0),
    (128, 128, 128),
    (255, 215, 0),
]

cursor_x = DISPLAY_W / 2
cursor_y = DISPLAY_H / 2
last_drawn_x = -1.0
last_drawn_y = -1.0

draw_state = {
    "current_color": 0,
    "is_drawing": False,
    "eraser_mode": False,
    "last_button_time": 0,
    "last_button_repeat_time": 0,
    "joystick_moving": False,
    "last_a_state": False,
    "last_b_state": False,
    "last_cursor_x": -1,
    "last_cursor_y": -1,
}

last_joy_value = [0.0, 0.0]


def read_joystick_axis(raw, axis_index):
    value = (raw - JOYSTICK_CENTER) / (JOYSTICK_MAX / 2)
    dead_zone_threshold = JOYSTICK_DEADZONE / (JOYSTICK_MAX / 2)

    if abs(value) >= dead_zone_threshold:
        if value > 1.0:
            value = 1.0
        if value < -1.0:
            value = -1.0
        sign = 1.0 if value >= 0 else -1.0
        value = sign * math.pow(abs(value), 1.0 / (1.0 + JOYSTICK_CURVE))
        last_joy_value[axis_index] = value
        return value

    if abs(last_joy_value[axis_index]) < dead_zone_threshold * 1.5:
        last_joy_value[axis_index] = 0.0
        return 0.0

    last_joy_value[axis_index] *= 0.9
    if abs(last_joy_value[axis_index]) < dead_zone_threshold:
        last_joy_value[axis_index] = 0.0
    return last_joy_value[axis_index]


def update_cursor():
    global cursor_x, cursor_y
    move_x = 0.0
    move_y = 0.0
    is_moving = False

    jx, jy = joy_read()
    joy_x = read_joystick_axis(jx, 0)
    # v4 stick: physical up reads higher ADC — negate so motion matches screen (like D-pad).
    joy_y = -read_joystick_axis(jy, 1)

    if abs(joy_x) > 0.0001 or abs(joy_y) > 0.0001:
        move_x += joy_x * CURSOR_SPEED
        move_y += joy_y * CURSOR_SPEED
        is_moving = True

    current_time = utime.ticks_ms()
    can_repeat = utime.ticks_diff(current_time, draw_state["last_button_repeat_time"]) >= BUTTON_REPEAT_DELAY

    if is_pressed(button_left) and can_repeat:
        move_x -= BUTTON_MOVE_SPEED
        is_moving = True
        draw_state["last_button_repeat_time"] = current_time
    if is_pressed(button_right) and can_repeat:
        move_x += BUTTON_MOVE_SPEED
        is_moving = True
        draw_state["last_button_repeat_time"] = current_time
    if is_pressed(button_up) and can_repeat:
        move_y -= BUTTON_MOVE_SPEED
        is_moving = True
        draw_state["last_button_repeat_time"] = current_time
    if is_pressed(button_down) and can_repeat:
        move_y += BUTTON_MOVE_SPEED
        is_moving = True
        draw_state["last_button_repeat_time"] = current_time

    if is_moving:
        cursor_x += move_x
        cursor_y += move_y
        if cursor_x < DRAW_AREA_MARGIN:
            cursor_x = DRAW_AREA_MARGIN
        if cursor_x >= DISPLAY_W - DRAW_AREA_MARGIN:
            cursor_x = DISPLAY_W - DRAW_AREA_MARGIN - 1
        if cursor_y < TOP_TEXT_MARGIN:
            cursor_y = TOP_TEXT_MARGIN
        if cursor_y >= DISPLAY_H - DRAW_AREA_MARGIN:
            cursor_y = DISPLAY_H - DRAW_AREA_MARGIN - 1

    draw_state["joystick_moving"] = is_moving
    return is_moving


def draw_pixels(prev_x, prev_y, curr_x, curr_y):
    color = st7789.BLACK if draw_state["eraser_mode"] else COLORS[draw_state["current_color"]]
    start_x = int(prev_x + 0.5)
    start_y = int(prev_y + 0.5)
    end_x = int(curr_x + 0.5)
    end_y = int(curr_y + 0.5)

    if start_x == end_x and start_y == end_y:
        tft.pixel(start_x, start_y, color)
        return

    dx = abs(end_x - start_x)
    dy = abs(end_y - start_y)
    sx = 1 if start_x < end_x else -1
    sy = 1 if start_y < end_y else -1
    err = dx - dy
    x = start_x
    y = start_y
    while True:
        tft.pixel(x, y, color)
        if x == end_x and y == end_y:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def clear_screen():
    global cursor_x, cursor_y, last_drawn_x, last_drawn_y
    tft.fill(st7789.BLACK)
    cursor_x = DISPLAY_W / 2
    cursor_y = DISPLAY_H / 2
    last_drawn_x = -1.0
    last_drawn_y = -1.0
    play_tone(400, 100)
    sleep(50)
    play_tone(300, 100)


def next_color():
    draw_state["current_color"] = (draw_state["current_color"] + 1) % NUM_COLORS
    draw_state["eraser_mode"] = False
    set_rgb_color(*RGB_COLORS[draw_state["current_color"]])
    play_tone(600 + (draw_state["current_color"] * 50), 50)


def toggle_eraser():
    draw_state["eraser_mode"] = not draw_state["eraser_mode"]
    if draw_state["eraser_mode"]:
        set_rgb_color(64, 64, 64)
        play_tone(300, 100)
    else:
        set_rgb_color(*RGB_COLORS[draw_state["current_color"]])
        play_tone(500, 100)


def draw_ui():
    tft.rect(0, 0, DISPLAY_W, DISPLAY_H, st7789.WHITE)
    tft.fill_rect(1, 1, DISPLAY_W - 2, TOP_TEXT_MARGIN - 1, st7789.BLACK)
    if draw_state["eraser_mode"]:
        tft.fill_rect(5, 5, 30, 10, st7789.BLACK)
        tft.rect(5, 5, 30, 10, st7789.WHITE)
    else:
        tft.fill_rect(5, 5, 30, 10, COLORS[draw_state["current_color"]])
    tft.fill_rect(38, 5, 100, 10, st7789.BLACK)
    label = "ERASER" if draw_state["eraser_mode"] else "C:" + str(draw_state["current_color"])
    tft.text(font, label, 38, 6, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A:Col B:Ers A+B:Clr", 120, 6, st7789.WHITE, st7789.BLACK)


def process_buttons():
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, draw_state["last_button_time"]) < BUTTON_DEBOUNCE:
        draw_state["last_a_state"] = is_pressed(button_A)
        draw_state["last_b_state"] = is_pressed(button_B)
        return

    a_pressed = is_pressed(button_A)
    b_pressed = is_pressed(button_B)
    a_just = a_pressed and not draw_state["last_a_state"]
    b_just = b_pressed and not draw_state["last_b_state"]
    draw_state["last_a_state"] = a_pressed
    draw_state["last_b_state"] = b_pressed

    if not a_just and not b_just:
        return

    if (a_just and b_pressed) or (b_just and a_pressed):
        clear_screen()
        draw_state["last_button_time"] = current_time
        draw_ui()
        return
    if a_just:
        next_color()
        draw_state["last_button_time"] = current_time
        draw_ui()
        return
    if b_just:
        toggle_eraser()
        draw_state["last_button_time"] = current_time
        draw_ui()
        return


def draw_cursor_box():
    x = int(cursor_x)
    y = int(cursor_y)
    if draw_state["last_cursor_x"] == x and draw_state["last_cursor_y"] == y:
        return
    if draw_state["last_cursor_x"] != -1 and draw_state["last_cursor_y"] != -1:
        tft.fill_rect(draw_state["last_cursor_x"] - 4, draw_state["last_cursor_y"] - 4, 9, 9, st7789.BLACK)
    tft.rect(x - 3, y - 3, 7, 7, st7789.WHITE)
    tft.rect(x - 2, y - 2, 5, 5, st7789.WHITE)
    draw_state["last_cursor_x"] = x
    draw_state["last_cursor_y"] = y


def setup():
    print("Etch-a-Sketch v4...")
    tft.fill(st7789.BLACK)
    set_rgb_color(*RGB_COLORS[draw_state["current_color"]])
    tft.text(font, "ETCH", 80, 100, st7789.CYAN, st7789.BLACK)
    tft.text(font, "A-SKETCH", 60, 120, st7789.CYAN, st7789.BLACK)
    tft.text(font, "Stick/Arrows: draw", 30, 160, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A+B: clear canvas", 30, 175, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A: color  B: eraser", 30, 190, st7789.WHITE, st7789.BLACK)
    play_tone(523, 200)
    sleep(100)
    play_tone(659, 200)
    sleep(100)
    play_tone(784, 300)
    utime.sleep(2)
    clear_screen()
    draw_ui()


def loop():
    global last_drawn_x, last_drawn_y
    while True:
        process_buttons()
        cursor_moving = update_cursor()

        if draw_state["eraser_mode"]:
            draw_cursor_box()
        else:
            if draw_state["last_cursor_x"] != -1 and draw_state["last_cursor_y"] != -1:
                tft.fill_rect(draw_state["last_cursor_x"] - 3, draw_state["last_cursor_y"] - 3, 7, 7, st7789.BLACK)
                draw_state["last_cursor_x"] = -1
                draw_state["last_cursor_y"] = -1

        if cursor_moving:
            if last_drawn_x < 0 or last_drawn_y < 0:
                color = st7789.BLACK if draw_state["eraser_mode"] else COLORS[draw_state["current_color"]]
                tft.pixel(int(cursor_x), int(cursor_y), color)
                last_drawn_x = cursor_x
                last_drawn_y = cursor_y
            elif last_drawn_x != cursor_x or last_drawn_y != cursor_y:
                draw_pixels(last_drawn_x, last_drawn_y, cursor_x, cursor_y)
                last_drawn_x = cursor_x
                last_drawn_y = cursor_y
        else:
            if last_drawn_x < 0 or last_drawn_y < 0:
                last_drawn_x = cursor_x
                last_drawn_y = cursor_y
            else:
                last_drawn_x = cursor_x
                last_drawn_y = cursor_y

        sleep(1)


try:
    setup()
    loop()
except Exception as e:
    print("Error in main:", e)
    raise
