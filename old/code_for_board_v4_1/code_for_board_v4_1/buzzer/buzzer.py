# Play a short scale on the piezo (GPIO 48).
from board_v4 import *

notes = (262, 294, 330, 349, 392, 440, 494, 523)
tft_init(include_status_bar=False)
print("Buzzer scale")
while True:
    for f in notes:
        play_tone(f, 180)
        sleep(40)
    sleep(600)
