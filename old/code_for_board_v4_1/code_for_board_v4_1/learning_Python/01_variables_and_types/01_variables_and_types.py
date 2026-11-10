# Lesson 1 — Variables and types.
#
# Show four common types (string, int, float, bool), then update values and print again.

# from board_v4 import * — then print() draws on the TFT (use builtins.print for USB serial).
from board_v4 import *

tft_init()
println_reset()

# Print starting message
print("Lesson 01 - Variables & Types")
sleep(1000)

# Create some variables
name = "e-Badge" # string
apples = 4       # integer
temp_c = 22.5    # floating point
ready = True     # Boolean

# Print each variable one at a time, with 1 second pauses
print(name)
sleep(1000)

print(apples)
sleep(1000)

print(temp_c)
sleep(1000)

print(ready)
sleep(1000)

# Integer operations, then print the modified int.
new_apples = 3
apples = apples + new_apples
sold_apples = 2
apples = apples - sold_apples

print("New number of apples:", apples)
sleep(1000)

# Convert Celsius to Fahrenheit, then print temp_f.
temp_f = (temp_c * 9.0 / 5.0) + 32.0
print("Temperature in Fahrenheit:", temp_f)
sleep(1000)

# String concat, then print the concatenated string.
message = "Hello " + name
print(message)
sleep(1000)

# Wait for B button to be pressed to exit the program.
print();
print("Waiting for B button press to exit...")
while not is_pressed(button_B):
    sleep(100)

