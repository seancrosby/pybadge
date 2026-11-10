# Snake — e-Badge v4 (learning_Python). Port of snake/snake-arduino.ino using board_v4.

import utime
import random

from board_v4 import (
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

GRID_W = 16
GRID_H = 14
CELL = 10
OFF_X = 10
OFF_Y = 18
MAX_SNAKE = GRID_W * GRID_H

BORDER_X = OFF_X - 2
BORDER_Y = OFF_Y - 2
BORDER_W = GRID_W * CELL + 2
BORDER_H = GRID_H * CELL + 2

BASE_TICK_MS = 320
MIN_TICK_MS = 110
SPEED_STEP_MS = 18
SPEED_EVERY = 4
INPUT_COOLDOWN_MS = 70
PAUSE_DEBOUNCE_MS = 200

JOY_CENTER = 2048
JOY_EDGE = 450

DARKGREEN = 0x0320

DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)

snake_x = [0] * MAX_SNAKE
snake_y = [0] * MAX_SNAKE
snake_len = 0
food_x = 0
food_y = 0
direction = 1
next_direction = 1
score = 0
game_over = False
paused = False
last_tick = 0
tick_interval = BASE_TICK_MS
last_input_time = 0

# wrap_mode True: dotted border, snake wraps at edges. False: solid border, walls kill.
wrap_mode = False
prev_a = False
prev_b = False
prev_combo = False


def draw_cell(gx, gy, color):
    sx = OFF_X + gx * CELL
    sy = OFF_Y + gy * CELL
    tft.fill_rect(sx, sy, CELL - 1, CELL - 1, color)


def draw_border():
    c = st7789.WHITE
    if not wrap_mode:
        tft.rect(BORDER_X, BORDER_Y, BORDER_W, BORDER_H, c)
        return
    dash = 5
    gap = 4
    step = dash + gap
    x1 = BORDER_X + BORDER_W - 1
    y1 = BORDER_Y + BORDER_H - 1
    for x in range(BORDER_X, BORDER_X + BORDER_W, step):
        xe = min(x + dash - 1, x1)
        if x <= xe:
            tft.line(x, BORDER_Y, xe, BORDER_Y, c)
            tft.line(x, y1, xe, y1, c)
    for y in range(BORDER_Y, BORDER_Y + BORDER_H, step):
        ye = min(y + dash - 1, y1)
        if y <= ye:
            tft.line(BORDER_X, y, BORDER_X, ye, c)
            tft.line(x1, y, x1, ye, c)


def draw_score():
    tft.fill_rect(188, 8, 125, 36, st7789.BLACK)
    tft.text(font, "Pts:", 188, 8, st7789.WHITE, st7789.BLACK)
    tft.text(font, str(score), 188, 24, st7789.WHITE, st7789.BLACK)


def draw_help():
    tft.text(font, "Stick/", 188, 48, st7789.CYAN, st7789.BLACK)
    tft.text(font, "Arrows:", 188, 56, st7789.CYAN, st7789.BLACK)
    tft.text(font, "Steer", 188, 68, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A:Pause", 188, 80, st7789.WHITE, st7789.BLACK)
    tft.text(font, "B:Wrap", 188, 92, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A+B:New", 188, 104, st7789.WHITE, st7789.BLACK)


def occupies_snake(x, y):
    for i in range(snake_len):
        if snake_x[i] == x and snake_y[i] == y:
            return True
    return False


def place_food():
    global food_x, food_y, game_over
    for _ in range(500):
        fx = random.randint(0, GRID_W - 1)
        fy = random.randint(0, GRID_H - 1)
        if not occupies_snake(fx, fy):
            food_x = fx
            food_y = fy
            draw_cell(food_x, food_y, st7789.RED)
            return
    game_over = True


def _wait_ab_new_game():
    while True:
        if is_pressed(button_A) and is_pressed(button_B):
            sleep(250)
            reset_game()
            return
        sleep(40)


def handle_you_win():
    tft.fill(st7789.BLACK)
    tft.text(font, "YOU WIN!", 40, 90, st7789.GREEN, st7789.BLACK)
    tft.text(font, "Score " + str(score), 50, 130, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A+B new game", 40, 200, st7789.WHITE, st7789.BLACK)
    set_rgb_color(0, 255, 0)
    play_tone(880, 200)
    sleep(150)
    play_tone(990, 250)
    _wait_ab_new_game()


def reset_game():
    global snake_len, direction, next_direction, score, game_over, paused
    global tick_interval, last_tick, snake_x, snake_y
    global prev_a, prev_b, prev_combo

    snake_len = 3
    snake_x[0] = 5
    snake_y[0] = 7
    snake_x[1] = 4
    snake_y[1] = 7
    snake_x[2] = 3
    snake_y[2] = 7
    direction = 1
    next_direction = 1
    score = 0
    game_over = False
    paused = False
    tick_interval = BASE_TICK_MS
    last_tick = utime.ticks_ms()

    tft.fill(st7789.BLACK)
    draw_border()
    for i in range(snake_len):
        c = st7789.GREEN if i == 0 else DARKGREEN
        draw_cell(snake_x[i], snake_y[i], c)
    place_food()
    draw_score()
    draw_help()
    set_rgb_color(0, 255, 100)

    prev_a = is_pressed(button_A)
    prev_b = is_pressed(button_B)
    prev_combo = prev_a and prev_b


def show_splash():
    tft.fill(st7789.BLACK)
    tft.text(font, "SNAKE", 70, 90, st7789.GREEN, st7789.BLACK)
    tft.text(font, "Stick / arrows: turn", 30, 125, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A: Pause  B: Wrap", 30, 140, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A+B: New game", 30, 155, st7789.WHITE, st7789.BLACK)
    sleep(2200)


def handle_game_over():
    tft.fill(st7789.BLACK)
    tft.text(font, "GAME", 70, 85, st7789.RED, st7789.BLACK)
    tft.text(font, "OVER", 70, 105, st7789.RED, st7789.BLACK)
    tft.text(font, "Score " + str(score), 60, 160, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A+B new game", 40, 200, st7789.WHITE, st7789.BLACK)
    set_rgb_color(255, 0, 0)
    play_tone(180, 900)
    _wait_ab_new_game()


def toggle_pause():
    global paused
    paused = not paused
    if paused:
        tft.fill_rect(72, 96, 136, 44, st7789.BLACK)
        tft.rect(71, 95, 138, 46, st7789.WHITE)
        tft.text(font, "PAUSED", 96, 108, st7789.YELLOW, st7789.BLACK)
        set_rgb_color(255, 255, 0)
    else:
        tft.fill_rect(71, 95, 138, 46, st7789.BLACK)
        draw_border()
        for i in range(snake_len):
            c = st7789.GREEN if i == 0 else DARKGREEN
            draw_cell(snake_x[i], snake_y[i], c)
        draw_cell(food_x, food_y, st7789.RED)
        draw_help()
        set_rgb_color(0, 255, 100)


def try_queue_direction(new_dir):
    global next_direction
    if (new_dir + 2) % 4 == direction:
        return
    next_direction = new_dir


def process_input():
    global last_input_time, prev_a, prev_b, prev_combo, wrap_mode

    t = utime.ticks_ms()
    a_now = is_pressed(button_A)
    b_now = is_pressed(button_B)
    combo = a_now and b_now

    if combo and not prev_combo:
        sleep(200)
        reset_game()
        last_input_time = utime.ticks_ms()
        prev_a = is_pressed(button_A)
        prev_b = is_pressed(button_B)
        prev_combo = prev_a and prev_b
        return

    if b_now and not a_now and not prev_b:
        wrap_mode = not wrap_mode
        draw_border()
        play_tone(520 if wrap_mode else 260, 70)
        last_input_time = t
        prev_a, prev_b, prev_combo = a_now, b_now, combo
        sleep(160)
        return

    if a_now and not b_now and not prev_a:
        toggle_pause()
        sleep(PAUSE_DEBOUNCE_MS)
        last_input_time = t
        prev_a, prev_b, prev_combo = a_now, b_now, combo
        return

    prev_a, prev_b, prev_combo = a_now, b_now, combo

    if paused or game_over:
        return

    if utime.ticks_diff(t, last_input_time) < INPUT_COOLDOWN_MS:
        return

    moved = False
    if is_pressed(button_up):
        try_queue_direction(0)
        moved = True
    elif is_pressed(button_right):
        try_queue_direction(1)
        moved = True
    elif is_pressed(button_down):
        try_queue_direction(2)
        moved = True
    elif is_pressed(button_left):
        try_queue_direction(3)
        moved = True
    else:
        vx, vy = joy_read()
        dx = vx - JOY_CENTER
        dy = vy - JOY_CENTER
        up = dy > JOY_EDGE
        down = dy < -JOY_EDGE
        right = dx > JOY_EDGE
        left = dx < -JOY_EDGE
        if up or down or right or left:
            if abs(dy) >= abs(dx):
                if up:
                    try_queue_direction(0)
                    moved = True
                elif down:
                    try_queue_direction(2)
                    moved = True
            else:
                if right:
                    try_queue_direction(1)
                    moved = True
                elif left:
                    try_queue_direction(3)
                    moved = True

    if moved:
        last_input_time = t
        play_tone(350, 25)


def game_tick():
    global direction, next_direction, snake_len, score, game_over, tick_interval

    direction = next_direction
    nx = snake_x[0] + DX[direction]
    ny = snake_y[0] + DY[direction]

    if wrap_mode:
        if nx < 0:
            nx = GRID_W - 1
        elif nx >= GRID_W:
            nx = 0
        if ny < 0:
            ny = GRID_H - 1
        elif ny >= GRID_H:
            ny = 0
    else:
        if nx < 0 or nx >= GRID_W or ny < 0 or ny >= GRID_H:
            game_over = True
            return

    for i in range(snake_len):
        if snake_x[i] == nx and snake_y[i] == ny:
            game_over = True
            return

    eating = nx == food_x and ny == food_y

    if not eating:
        draw_cell(snake_x[snake_len - 1], snake_y[snake_len - 1], st7789.BLACK)
        for i in range(snake_len - 1, 0, -1):
            snake_x[i] = snake_x[i - 1]
            snake_y[i] = snake_y[i - 1]
    else:
        if snake_len >= MAX_SNAKE:
            game_over = True
            return
        snake_len += 1
        for i in range(snake_len - 1, 0, -1):
            snake_x[i] = snake_x[i - 1]
            snake_y[i] = snake_y[i - 1]
        score += 10
        draw_score()
        play_tone(660, 60)
        if score > 0 and score % (SPEED_EVERY * 10) == 0 and tick_interval > MIN_TICK_MS:
            tick_interval -= SPEED_STEP_MS

    snake_x[0] = nx
    snake_y[0] = ny

    draw_cell(snake_x[1], snake_y[1], DARKGREEN)
    draw_cell(snake_x[0], snake_y[0], st7789.GREEN)

    if eating:
        place_food()
        set_rgb_color(0, 200, 255)
        sleep(15)
        set_rgb_color(0, 255, 100)


def setup():
    jx, jy = joy_read()
    random.seed(jx ^ jy ^ utime.ticks_ms())
    show_splash()
    reset_game()


def loop():
    global last_tick
    while True:
        if game_over:
            if snake_len >= MAX_SNAKE:
                handle_you_win()
            else:
                handle_game_over()
            continue

        process_input()

        if not paused:
            now = utime.ticks_ms()
            if utime.ticks_diff(now, last_tick) >= tick_interval:
                last_tick = now
                game_tick()

        sleep(5)


try:
    setup()
    loop()
except Exception as e:
    print("Error in main:", e)
    raise
