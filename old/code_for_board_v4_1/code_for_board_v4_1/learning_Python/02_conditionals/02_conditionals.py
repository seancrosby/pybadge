# Lesson 2 — Conditions: if, comparisons (>, <, >=, <=), and booleans (and, or, not).
#
# An "if" runs the indented block only when the condition is True. This lesson lights
# LEDs on the ring so you can see which conditions are active. At startup, one print
# line explains each pixel index; the loop does not re-print that list. LEDs 10–11 use
# the joystick X; LEDs 12–13 use how many of the six buttons are pressed at once.

# Use print(...) for the console (like Python on a PC). Bottom strip = live inputs.
from board_v4 import *

# TH is a "threshold" number for the joystick X reading. Move the stick left/right
# and watch LEDs 10 and 11 swap as vx crosses this value. For LEDs 12–13 we count how
# many of the six face buttons are held at once (0 .. 6) and compare with >= and <=.
TH = 2000
BTN_GE = 2  # px12 lights when this many or more buttons are pressed
BTN_LE = 1  # px13 lights when this many or fewer buttons are pressed

tft_init(include_status_bar=True)
addr_clear()

# Print starting message
print("Lesson 02 - Conditionals")
sleep(1000)

println_reset()
print("px0:  A btn     | px1:  B btn")
print("px2:  Up btn    | px3:  A and B")
print("px4:  A or B    | px5:  A xor B")
print("px6:  not A     | px7:  A and B and Up")
print("px8:  A nand B  | px9:  A nor B")
print("px10: vx > TH   | px11: vx < TH")
print("px12: btn >= 2  | px13: btn <= 1")

while True:
    # Read all the inputs once per loop; we use these names in the conditions below.
    on_a = is_pressed(button_A)
    on_b = is_pressed(button_B)
    on_u = is_pressed(button_up)
    on_d = is_pressed(button_down)
    on_l = is_pressed(button_left)
    on_r = is_pressed(button_right)
    vx, _ = joy_read() # vx is the joystick X reading, _ is the joystick Y reading.

    # Button count: count how many buttons are pressed.
    btn_count = int(on_a) + int(on_b) + int(on_u) + int(on_d) + int(on_l) + int(on_r)

    # Clear the strip buffer (no write yet), set pixels for this frame, then one write.
    addr_blank()

    # Simple "if button then light this LED" — three separate checks (not elif),
    # so more than one can be true at once.
    if on_a:
        px(0, RED)
    if on_b:
        px(1, RED)
    if on_u:
        px(2, RED)

    # Boolean combinations: "and" needs both true, "or" needs at least one true.
    if on_a and on_b:
        px(3, RED)
    if on_a or on_b:
        px(4, RED)
    # XOR feel: exactly one of A or B (exclusive or), written out with and/or/not.
    if (on_a and not on_b) or (not on_a and on_b):
        px(5, RED)

    # NOT A: lights when A is not pressed.
    if not on_a:
        px(6, RED)

    # A and B and Up: lights when A, B, and Up are all pressed.
    if on_a and on_b and on_u:
        px(7, RED)

    # NAND: not (both A and B). NOR: not (A or B).
    if not (on_a and on_b):
        px(8, RED)

    # NOR: not (A or B).
    if not (on_a or on_b):
        px(9, RED)

    # Joystick X vs TH (>), (<). How many buttons pressed: (>=), (<=).
    if vx > TH:
        px(10, RED)
    if vx < TH:
        px(11, RED)

    # Button count: (>=), (<=).
    if btn_count >= BTN_GE:
        px(12, RED)
    if btn_count <= BTN_LE:
        px(13, RED)

    # Send the LED colors we built to the hardware.
    addr_show()

    # Refresh only the small bottom strip (no full-screen redraw).
    update_status_bar()

    sleep(80)
