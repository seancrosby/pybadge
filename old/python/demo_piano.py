"""Six-button piano demo using the beginner-friendly ebadge module."""

import ebadge


# One melody note per physical button. The buzzer plays one note at a time.
NOTES = (
    (ebadge.button_a, "C4", 262, 1, ebadge.RED),
    (ebadge.button_b, "D4", 294, 5, ebadge.ORANGE),
    (ebadge.button_up, "E4", 330, 9, ebadge.YELLOW),
    (ebadge.button_down, "F4", 349, 13, ebadge.GREEN),
    (ebadge.button_left, "G4", 392, 17, ebadge.CYAN),
    (ebadge.button_right, "A4", 440, 21, ebadge.PURPLE),
)


def show_welcome():
    """Draw the welcome screen and the button-to-note guide."""
    ebadge.display_clear()
    ebadge.draw_rectangle(12, 18, 296, 204, ebadge.CYAN)
    ebadge.display_text("Welcome to the", 88, 38, ebadge.WHITE)
    ebadge.display_text("eBadge Piano!", 88, 62, ebadge.YELLOW)
    ebadge.draw_line(36, 92, 284, 92, ebadge.BLUE)
    ebadge.display_text("Press and hold a button", 64, 108, ebadge.WHITE)
    ebadge.display_text("A:C4  B:D4  Up:E4", 64, 142, ebadge.GREEN)
    ebadge.display_text("Down:F4  Left:G4", 64, 164, ebadge.CYAN)
    ebadge.display_text("Right:A4", 64, 186, ebadge.PURPLE)


def show_note(note):
    """Show the currently playing note."""
    _button, name, frequency, _first_pixel, color = note
    ebadge.display_clear()
    ebadge.display_text("eBadge Piano", 88, 36, ebadge.CYAN)
    ebadge.draw_line(36, 64, 284, 64, ebadge.BLUE)
    ebadge.display_text("Now playing", 104, 94, ebadge.WHITE)
    ebadge.display_text(name, 136, 122, color)
    ebadge.display_text("%d Hz" % frequency, 128, 152, ebadge.WHITE)
    ebadge.display_text("Release to stop", 96, 190, ebadge.YELLOW)


def light_note(note):
    """Light three pixels around the note's position on the ring."""
    _button, _name, _frequency, first_pixel, color = note
    for offset in range(3):
        ebadge.set_pixel(first_pixel + offset, color)


def main():
    """Initialize the badge and play notes while their buttons are held."""
    ebadge.initialize()
    ebadge.clear_pixels()
    ebadge.turn_led_off()
    show_welcome()
    active_note = None

    while True:
        pressed_note = None
        for note in NOTES:
            if ebadge.is_pressed(note[0]):
                pressed_note = note
                break

        if pressed_note is None:
            if active_note is not None:
                ebadge.play_tone(0, 1)
                ebadge.clear_pixels()
                active_note = None
                show_welcome()
            ebadge.pause(20)
            continue

        if pressed_note != active_note:
            ebadge.clear_pixels()
            show_note(pressed_note)
            light_note(pressed_note)
            active_note = pressed_note

        # Short tone segments keep the button and note display responsive.
        ebadge.play_tone(pressed_note[2], 80)


main()
