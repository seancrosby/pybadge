# Lesson 3 — if / elif / else: only ONE branch runs (first True condition wins).
#
# Unlike several separate "if" lines, elif chains behave like a decision ladder:
# Python checks from top to bottom and runs the first block whose condition is True.
# If none are True, "else" runs.

from board_v4 import *

tft_init(include_status_bar=True)

# Print starting message
print("Lesson 03 - If/Else Chains")
sleep(1000)

while True:
    on_a = is_pressed(button_A)
    on_b = is_pressed(button_B)

    # First condition that is true wins; the rest of the chain is skipped.
    if on_a and on_b:
        msg = "Both"
        set_rgb_color(YELLOW)
    elif on_a:
        msg = "A"
        set_rgb_color(GREEN)
    elif on_b:
        msg = "B"
        set_rgb_color(RED)
    else:
        # Neither A nor B is pressed.
        msg = "—"
        rgb_off()

    # Show the label for whichever branch ran (same idea every time through the loop).
    println_reset()
    print(msg)
    sleep(80)
