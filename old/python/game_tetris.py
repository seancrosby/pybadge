# Tetris — e-Badge v4 (learning_Python). Port of tetris/tetris-micropython using board_v4.
# Needs st7789py.py + font next to this file (same as other lessons).

import utime
import random
from time import sleep_ms

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

# Game constants
GRID_WIDTH = 10
GRID_HEIGHT = 18
BLOCK_SIZE = 11
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 15
BUTTON_DELAY = 150  # ms
NORMAL_MOVE_DELAY = 500  # ms
FAST_MOVE_DELAY = 50  # ms
PAUSE_DEBOUNCE = 200  # ms
LINE_FLASH_DELAY = 50  # ms
LINE_FLASH_COUNT = 6
POINTS_PER_LINE = 100

JOY_CENTER = 2048
JOY_EDGE = 450

# Color definitions (RGB565)
COLORS = [
    0x07FF,  # Cyan
    0xFFE0,  # Yellow
    0xF81F,  # Magenta
    0x07E0,  # Green
    0xF800,  # Red
    0x001F,  # Blue
    0xFD20   # Orange
]

# RGB LED colors (8-bit)
RGB_COLORS = [
    (0, 255, 255),    # Cyan
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta
    (0, 255, 0),      # Green
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (255, 165, 0)     # Orange
]

# Tetromino shapes
SHAPES = [
    # I
    [[[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
     [[0,0,1,0], [0,0,1,0], [0,0,1,0], [0,0,1,0]],
     [[0,0,0,0], [0,0,0,0], [1,1,1,1], [0,0,0,0]],
     [[0,1,0,0], [0,1,0,0], [0,1,0,0], [0,1,0,0]]],
    # O
    [[[0,1,1,0], [0,1,1,0], [0,0,0,0], [0,0,0,0]],
     [[0,1,1,0], [0,1,1,0], [0,0,0,0], [0,0,0,0]],
     [[0,1,1,0], [0,1,1,0], [0,0,0,0], [0,0,0,0]],
     [[0,1,1,0], [0,1,1,0], [0,0,0,0], [0,0,0,0]]],
    # T
    [[[0,1,0,0], [1,1,1,0], [0,0,0,0], [0,0,0,0]],
     [[0,1,0,0], [0,1,1,0], [0,1,0,0], [0,0,0,0]],
     [[0,0,0,0], [1,1,1,0], [0,1,0,0], [0,0,0,0]],
     [[0,1,0,0], [1,1,0,0], [0,1,0,0], [0,0,0,0]]],
    # S
    [[[0,1,1,0], [1,1,0,0], [0,0,0,0], [0,0,0,0]],
     [[0,1,0,0], [0,1,1,0], [0,0,1,0], [0,0,0,0]],
     [[0,0,0,0], [0,1,1,0], [1,1,0,0], [0,0,0,0]],
     [[1,0,0,0], [1,1,0,0], [0,1,0,0], [0,0,0,0]]],
    # Z
    [[[1,1,0,0], [0,1,1,0], [0,0,0,0], [0,0,0,0]],
     [[0,0,1,0], [0,1,1,0], [0,1,0,0], [0,0,0,0]],
     [[0,0,0,0], [1,1,0,0], [0,1,1,0], [0,0,0,0]],
     [[0,1,0,0], [1,1,0,0], [1,0,0,0], [0,0,0,0]]],
    # J
    [[[1,0,0,0], [1,1,1,0], [0,0,0,0], [0,0,0,0]],
     [[0,1,1,0], [0,1,0,0], [0,1,0,0], [0,0,0,0]],
     [[0,0,0,0], [1,1,1,0], [0,0,1,0], [0,0,0,0]],
     [[0,1,0,0], [0,1,0,0], [1,1,0,0], [0,0,0,0]]],
    # L
    [[[0,0,1,0], [1,1,1,0], [0,0,0,0], [0,0,0,0]],
     [[0,1,0,0], [0,1,0,0], [0,1,1,0], [0,0,0,0]],
     [[0,0,0,0], [1,1,1,0], [1,0,0,0], [0,0,0,0]],
     [[1,1,0,0], [0,1,0,0], [0,1,0,0], [0,0,0,0]]]
]

# Game state
grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
game_state = {
    'last_move_time': 0,
    'last_button_time': 0,
    'move_delay': NORMAL_MOVE_DELAY,
    'score': 0,
    'is_over': False,
    'is_paused': False,
    'current_piece': {'type': 0, 'rotation': 0, 'x': 0, 'y': 0, 'color': 0},
    'prev_piece': {'x': 0, 'y': 0, 'rotation': 0}
}

def draw_block(x, y, color_idx):
    """Draw a single block on the display."""
    if color_idx > 0:
        color = COLORS[color_idx - 1]
    else:
        color = st7789.BLACK
    tft.fill_rect(
        GRID_OFFSET_X + x * BLOCK_SIZE,
        GRID_OFFSET_Y + y * BLOCK_SIZE,
        BLOCK_SIZE - 1,
        BLOCK_SIZE - 1,
        color
    )

def draw_grid():
    """Draw the entire game grid."""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            draw_block(x, y, grid[y][x])

def draw_current_piece():
    """Draw the current falling piece."""
    piece = SHAPES[game_state['current_piece']['type']][game_state['current_piece']['rotation']]
    x = game_state['current_piece']['x']
    y = game_state['current_piece']['y']
    color_idx = game_state['current_piece']['color'] + 1
    for py in range(4):
        for px in range(4):
            if piece[py][px]:
                grid_x = x + px
                grid_y = y + py
                if grid_y >= 0 and grid_y < GRID_HEIGHT and grid_x >= 0 and grid_x < GRID_WIDTH:
                    draw_block(grid_x, grid_y, color_idx)

def erase_previous_piece():
    """Erase the previous piece position."""
    piece = SHAPES[game_state['current_piece']['type']][game_state['prev_piece']['rotation']]
    x = game_state['prev_piece']['x']
    y = game_state['prev_piece']['y']
    for py in range(4):
        for px in range(4):
            if piece[py][px]:
                grid_x = x + px
                grid_y = y + py
                if grid_y >= 0 and grid_y < GRID_HEIGHT and grid_x >= 0 and grid_x < GRID_WIDTH:
                    draw_block(grid_x, grid_y, grid[grid_y][grid_x])

def draw_score():
    """Draw the score display."""
    tft.fill_rect(200, 10, 110, 30, st7789.BLACK)
    tft.text(font, "Score:", 200, 10, st7789.WHITE, st7789.BLACK)
    tft.text(font, str(game_state['score']), 200, 20, st7789.WHITE, st7789.BLACK)

def draw_controls():
    """Draw the control instructions."""
    tft.text(font, "Controls:", 200, 55, st7789.CYAN, st7789.BLACK)
    tft.text(font, "L/R stick", 200, 68, st7789.WHITE, st7789.BLACK)
    tft.text(font, "or D-pad", 200, 80, st7789.WHITE, st7789.BLACK)
    tft.text(font, "Up: Rot", 200, 92, st7789.WHITE, st7789.BLACK)
    tft.text(font, "Dn: Drop", 200, 104, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A: Pause", 200, 116, st7789.WHITE, st7789.BLACK)
    tft.text(font, "B: New", 200, 128, st7789.WHITE, st7789.BLACK)

def draw_border():
    """Draw the game grid border."""
    tft.rect(
        GRID_OFFSET_X - 2,
        GRID_OFFSET_Y - 2,
        GRID_WIDTH * BLOCK_SIZE + 2,
        GRID_HEIGHT * BLOCK_SIZE + 2,
        st7789.WHITE
    )

def check_collision(offset_x, offset_y, rotation):
    """Check if piece collides with walls or other pieces."""
    piece = SHAPES[game_state['current_piece']['type']][rotation]
    x = game_state['current_piece']['x'] + offset_x
    y = game_state['current_piece']['y'] + offset_y
    for py in range(4):
        for px in range(4):
            if piece[py][px]:
                grid_x = x + px
                grid_y = y + py
                if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT:
                    return True
                if grid_y >= 0 and grid[grid_y][grid_x]:
                    return True
    return False

def lock_piece():
    """Lock the current piece into the grid."""
    piece = SHAPES[game_state['current_piece']['type']][game_state['current_piece']['rotation']]
    x = game_state['current_piece']['x']
    y = game_state['current_piece']['y']
    color_idx = game_state['current_piece']['color'] + 1
    for py in range(4):
        for px in range(4):
            if piece[py][px]:
                grid_x = x + px
                grid_y = y + py
                if grid_y >= 0 and grid_y < GRID_HEIGHT and grid_x >= 0 and grid_x < GRID_WIDTH:
                    grid[grid_y][grid_x] = color_idx

def clear_lines():
    """Clear completed lines and update score."""
    global grid
    lines_cleared = 0
    y = GRID_HEIGHT - 1
    while y >= 0:
        if all(grid[y][x] > 0 for x in range(GRID_WIDTH)):
            lines_cleared += 1
            # Flash effect
            for flash in range(LINE_FLASH_COUNT):
                flash_color = st7789.GREEN if flash % 2 == 0 else st7789.BLUE
                for x in range(GRID_WIDTH):
                    draw_block(x, y, COLORS.index(flash_color) + 1 if flash_color in COLORS else 0)
                set_rgb_color(0, 255, 0) if flash % 2 == 0 else set_rgb_color(0, 0, 255)
                sleep_ms(LINE_FLASH_DELAY)
            # Move lines down
            for move_y in range(y, 0, -1):
                for x in range(GRID_WIDTH):
                    grid[move_y][x] = grid[move_y - 1][x]
            for x in range(GRID_WIDTH):
                grid[0][x] = 0
        else:
            y -= 1
    if lines_cleared > 0:
        game_state['score'] += lines_cleared * POINTS_PER_LINE
        play_tone(800, 100)
        draw_score()
        # Restore LED to current piece color
        set_rgb_color(*RGB_COLORS[game_state['current_piece']['color']])

def spawn_new_piece():
    """Spawn a new random piece."""
    piece_type = random.randint(0, 6)
    game_state['current_piece'] = {
        'type': piece_type,
        'rotation': 0,
        'x': 3,
        'y': 0,
        'color': piece_type
    }
    game_state['prev_piece'] = {
        'x': 3,
        'y': 0,
        'rotation': 0
    }
    set_rgb_color(*RGB_COLORS[piece_type])
    if check_collision(0, 0, 0):
        game_state['is_over'] = True

def reset_game():
    """Reset the game state."""
    global grid
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    game_state['score'] = 0
    game_state['is_over'] = False
    game_state['is_paused'] = False
    game_state['move_delay'] = NORMAL_MOVE_DELAY
    tft.fill(st7789.BLACK)
    draw_border()
    draw_grid()
    spawn_new_piece()
    draw_current_piece()
    draw_score()
    draw_controls()

def handle_game_over():
    """Draw game over screen."""
    tft.fill(st7789.BLACK)
    tft.text(font, "GAME", 80, 100, st7789.RED, st7789.BLACK)
    tft.text(font, "OVER", 80, 120, st7789.RED, st7789.BLACK)
    tft.text(font, "Score: " + str(game_state['score']), 60, 160, st7789.WHITE, st7789.BLACK)
    tft.text(font, "Press B for New Game", 50, 180, st7789.WHITE, st7789.BLACK)
    set_rgb_color(255, 0, 0)
    play_tone(200, 1000)

def toggle_pause():
    """Toggle pause state."""
    game_state['is_paused'] = not game_state['is_paused']
    if game_state['is_paused']:
        tft.fill_rect(80, 100, 120, 40, st7789.BLACK)
        tft.rect(79, 99, 122, 42, st7789.WHITE)
        tft.text(font, "PAUSED", 100, 110, st7789.YELLOW, st7789.BLACK)
        set_rgb_color(255, 255, 0)
    else:
        tft.fill_rect(79, 99, 122, 42, st7789.BLACK)
        draw_border()
        draw_grid()
        draw_current_piece()
        draw_controls()
        set_rgb_color(*RGB_COLORS[game_state['current_piece']['color']])

def setup():
    """MicroPython equivalent of Arduino setup()."""
    print("Starting Tetris (board v4)...")

    tft.fill(st7789.BLACK)

    jx, jy = joy_read()
    random.seed(jx ^ jy)

    # Show splash screen
    tft.text(font, "TETRIS", 60, 100, st7789.GREEN, st7789.BLACK)
    tft.text(font, "Stick or arrows", 40, 140, st7789.WHITE, st7789.BLACK)
    tft.text(font, "Move / rotate / drop", 40, 155, st7789.WHITE, st7789.BLACK)
    tft.text(font, "A: Pause  B: New", 40, 170, st7789.WHITE, st7789.BLACK)

    utime.sleep(3)
    reset_game()
    print("Game initialized!")

def loop():
    """Main game loop."""
    while True:
        if game_state['is_over']:
            handle_game_over()
            while True:
                if is_pressed(button_B):
                    sleep_ms(200)
                    reset_game()
                    break
                sleep_ms(50)
            continue

        current_time = utime.ticks_ms()

        # Process input
        if utime.ticks_diff(current_time, game_state['last_button_time']) >= BUTTON_DELAY:
            piece_moved = False

            # A button toggles pause
            if is_pressed(button_A):
                toggle_pause()
                game_state['last_button_time'] = current_time
                sleep_ms(PAUSE_DEBOUNCE)
                continue

            # B button starts new game
            if is_pressed(button_B):
                sleep_ms(200)
                reset_game()
                continue

            # Don't process other inputs if paused
            if not game_state['is_paused']:
                vx, vy = joy_read()
                jdx = vx - JOY_CENTER
                jdy = vy - JOY_CENTER
                joy_up = jdy > JOY_EDGE
                joy_down = jdy < -JOY_EDGE
                joy_right = jdx > JOY_EDGE
                joy_left = jdx < -JOY_EDGE

                if (is_pressed(button_left) or joy_left) and not check_collision(-1, 0, game_state['current_piece']['rotation']):
                    game_state['prev_piece']['x'] = game_state['current_piece']['x']
                    game_state['prev_piece']['y'] = game_state['current_piece']['y']
                    game_state['prev_piece']['rotation'] = game_state['current_piece']['rotation']
                    game_state['current_piece']['x'] -= 1
                    play_tone(400, 50)
                    game_state['last_button_time'] = current_time
                    piece_moved = True

                if (is_pressed(button_right) or joy_right) and not check_collision(1, 0, game_state['current_piece']['rotation']):
                    game_state['prev_piece']['x'] = game_state['current_piece']['x']
                    game_state['prev_piece']['y'] = game_state['current_piece']['y']
                    game_state['prev_piece']['rotation'] = game_state['current_piece']['rotation']
                    game_state['current_piece']['x'] += 1
                    play_tone(450, 50)
                    game_state['last_button_time'] = current_time
                    piece_moved = True

                if is_pressed(button_down) or joy_down:
                    game_state['move_delay'] = FAST_MOVE_DELAY
                else:
                    game_state['move_delay'] = NORMAL_MOVE_DELAY

                if is_pressed(button_up) or joy_up:
                    new_rotation = (game_state['current_piece']['rotation'] + 1) % 4
                    if not check_collision(0, 0, new_rotation):
                        game_state['prev_piece']['x'] = game_state['current_piece']['x']
                        game_state['prev_piece']['y'] = game_state['current_piece']['y']
                        game_state['prev_piece']['rotation'] = game_state['current_piece']['rotation']
                        game_state['current_piece']['rotation'] = new_rotation
                        play_tone(500, 50)
                        game_state['last_button_time'] = current_time
                        piece_moved = True

                if piece_moved:
                    erase_previous_piece()
                    draw_current_piece()

        # Update game (piece falling)
        if not game_state['is_paused']:
            if utime.ticks_diff(current_time, game_state['last_move_time']) >= game_state['move_delay']:
                if not check_collision(0, 1, game_state['current_piece']['rotation']):
                    game_state['prev_piece']['x'] = game_state['current_piece']['x']
                    game_state['prev_piece']['y'] = game_state['current_piece']['y']
                    game_state['prev_piece']['rotation'] = game_state['current_piece']['rotation']
                    game_state['current_piece']['y'] += 1
                    erase_previous_piece()
                    draw_current_piece()
                else:
                    lock_piece()
                    clear_lines()
                    spawn_new_piece()
                    draw_grid()
                    draw_current_piece()
                game_state['last_move_time'] = current_time

        sleep_ms(10)

try:
    setup()
    loop()
except Exception as e:
    print("Error in main:", e)
    raise
