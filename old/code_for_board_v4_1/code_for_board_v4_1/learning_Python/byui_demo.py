"""BYU-I demo for e-Badge v4.

Ported from the Arduino demo-programs BYU-I mode:
- BYU-I splash screen
- rotating blue/white addressable LED patterns
- press B to exit back to boot menu
"""

from board_v4 import *

PAT_MS = 7000
BYU_BLUE = (0, 70, 255)
BYU_WHITE = (235, 238, 255)


def _fill_all(color):
    r, g, b = color
    for i in range(NUM_ADDR_LEDS):
        addr_set(i, r, g, b)


def draw_splash():
    tft.fill(st7789.BLACK)
    tft.text(font, "BYU-I", 10, 8, 0x7DBF, st7789.BLACK)
    tft.text(font, "Computer", 10, 88, st7789.WHITE, st7789.BLACK)
    tft.text(font, "Science and", 10, 106, st7789.WHITE, st7789.BLACK)
    tft.text(font, "Engineering", 10, 124, st7789.WHITE, st7789.BLACK)
    tft.text(font, "Department", 10, 142, st7789.WHITE, st7789.BLACK)
    tft.text(font, "B: Back", 10, 220, 0x8410, st7789.BLACK)


def draw_pattern(t_ms):
    pat = (t_ms // PAT_MS) % 5
    addr_blank()

    if pat == 0:
        phase_ms = t_ms % (280 * 3)
        blue_phase = phase_ms < (280 * 2)
        _fill_all(BYU_BLUE if blue_phase else BYU_WHITE)

    elif pat == 1:
        head = (t_ms // 48) % NUM_ADDR_LEDS
        addr_set(head, *BYU_WHITE)
        addr_set((head + 1) % NUM_ADDR_LEDS, *BYU_BLUE)
        addr_set((head + 2) % NUM_ADDR_LEDS, *BYU_BLUE)

    elif pat == 2:
        shift = (t_ms // 70) % NUM_ADDR_LEDS
        for i in range(NUM_ADDR_LEDS):
            wave = (i + shift) % 3
            addr_set(i, *(BYU_BLUE if wave < 2 else BYU_WHITE))

    elif pat == 3:
        shift = (t_ms // 380) % NUM_ADDR_LEDS
        for i in range(NUM_ADDR_LEDS):
            tri = (i + shift) % 3
            addr_set(i, *(BYU_BLUE if tri < 2 else BYU_WHITE))

    else:
        # Soft pulse close to the Arduino version's beatsin brightness modulation.
        br = 28 + ((t_ms // 40) % 228)
        if ((t_ms // 1800) % 2) == 1:
            br = 255 - br
        pulse = (
            (BYU_WHITE[0] * br) // 255,
            (BYU_WHITE[1] * br) // 255,
            (BYU_BLUE[2] * br) // 255,
        )
        _fill_all(pulse)

    addr_show()


def main():
    tft_init()
    rgb_off()
    draw_splash()

    last_b = is_pressed(button_B)
    while True:
        b = is_pressed(button_B)
        if b and not last_b:
            break
        last_b = b
        draw_pattern(utime.ticks_ms())
        sleep(30)

    addr_clear()
    rgb_off()
    raise SystemExit


main()
