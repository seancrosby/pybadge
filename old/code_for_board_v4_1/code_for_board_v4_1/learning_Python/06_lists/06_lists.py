# Lesson 6 — Lists: ordered values; [0], [1], …; len(); for loops over a list.
#
# A list keeps many values in order. You pick one with an index: names[0] is the
# first item. len(names) is how many items there are. This lesson also uses two
# lists side by side: the same index picks a color name and its RGB triple.

from board_v4 import *

tft_init()

# Print starting message
print("Lesson 06 - Lists")
sleep(1000)

# Two parallel lists: index 0 goes with index 0, index 1 with 1, and so on.
names = ["red", "green", "blue", "yellow"]
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

# Walk the whole list once: same index i for name and color.
println_reset()
print("for i in range(len(names)):")
for i in range(len(names)):
    set_rgb_color(colors[i])
    print(names[i])
    sleep(1000)

# Interactive part: left/right change which list item is selected.
idx = 0
# "was_left" remembers the button state last time — we only want to move when
# you *first* press, not every loop while your finger is down.
was_left = False
was_right = False

while True:
    left = is_pressed(button_left)
    right = is_pressed(button_right)

    # Edge detect: button is pressed now, but was not pressed last frame.
    if left and not was_left:
        idx = idx - 1
        if idx < 0:
            # Wrap to the end of the list instead of going negative.
            idx = len(names) - 1
    if right and not was_right:
        idx = idx + 1
        if idx >= len(names):
            idx = 0

    was_left = left
    was_right = right

    # Show the color for the current index on the RGB LED and the name on screen.
    set_rgb_color(colors[idx])

    println_reset()
    print(names[idx])
    sleep(50)
