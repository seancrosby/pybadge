# Lesson 5 — def defines a function; return sends a value back (or you can just do an effect).
#
# A function is a named chunk of code you can call from many places. Some functions
# compute a value and use "return" to hand it back. Others just do something (like
# beep) and do not need return. Below, each return value is saved in a variable, then
# printed, with a 1 second pause between demos.

from board_v4 import *


def square(x):
    """One parameter; returns one number."""
    return x * x


def add(a, b):
    """Two parameters."""
    return a + b


def double(n):
    """Return doubles the input."""
    return n * 2


def max2(a, b):
    """Using if inside a function, then return."""
    if a > b:
        return a
    return b


def greeting(name):
    """Return a string built from the argument."""
    return "Hi, " + str(name)


def beep_twice():
    """No return — does something you can hear (a side effect)."""
    play_tone(523, 60)
    play_tone(659, 60)


tft_init(include_status_bar=True)
println_reset()

# Print starting message
print("Lesson 05 - Functions")
sleep(1000)

# Store the return value in a variable first, then print it. Pause 1 second between
# each demo so you can read the screen (sleep(1000) waits 1 second; arg is milliseconds).
r = square(5)
print("square(5) =", r)
sleep(1000)

r = add(10, 3)
print("add(10, 3) =", r)
sleep(1000)

r = double(4)
print("double(4) =", r)
sleep(1000)

r = max2(7, 12)
print("max2(7, 12) =", r)
sleep(1000)

msg = greeting("badge")
print(msg)
sleep(1000)

print("beep_twice() (no return value — Python uses None)...")
out = beep_twice()
print("returned:", out)
sleep(1000)

print("done.")
