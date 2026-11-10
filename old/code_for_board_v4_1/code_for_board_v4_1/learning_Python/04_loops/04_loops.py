# Lesson 4 — for: repeat a fixed count; while: repeat until False.
#
# Part 1: a for loop runs exactly five times — here, five short beeps.
# Part 2: another for loop walks every ring LED index (0 .. last) and lights one at a time.
# Part 3: a while loop keeps running until you press A; inside it we flip the big RGB LED on/off.

from board_v4 import *

tft_init()
addr_clear()

# Print starting message
print("Lesson 04 - Loops")
sleep(1000)

# --- Part 1: for — five beeps (same code body, counted by n = 0,1,2,3,4) ---
println_reset()
print("For loop test, beep buzzer 5 times...")
for n in range(5):
    play_tone(523, 80)
    sleep(1000)

# --- Part 2: for — one ring pixel at a time (only that LED is on) ---
println_reset()
print("For loop test:")
print("Go through all addr LEDs, one at a time ...")
for i in range(NUM_ADDR_LEDS):
    addr_blank()
    px(i, CYAN)
    addr_show()
    sleep(500)

addr_clear()

# --- Part 3: while — blink RGB until you press A ---
println_reset()
print("While loop test:")
print("LED blinks until button A pressed ...")
led_on = True
while not is_pressed(button_A):
    if led_on:
        set_rgb_color(0, 160, 120)
    else:
        rgb_off()
    led_on = not led_on
    sleep(250)

rgb_off()
play_tone(784, 120)
