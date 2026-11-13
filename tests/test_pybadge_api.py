"""Tests for the beginner-facing API using the headless backend."""

import sys

import pytest

import pybadge


def test_fixture_selects_headless_test_mode(badge_backend):
    assert pybadge.current_mode() == "test"
    assert badge_backend.initialized
    assert "backends.simulator_backend" not in sys.modules


def test_button_state_can_be_controlled(badge_backend):
    assert pybadge.is_pressed(pybadge.BUTTON_A) is False

    badge_backend.press_button(pybadge.BUTTON_A)
    assert pybadge.is_pressed(pybadge.BUTTON_A) is True

    badge_backend.release_button(pybadge.BUTTON_A)
    assert pybadge.is_pressed(pybadge.BUTTON_A) is False


def test_button_rejects_unknown_name(badge_backend):
    with pytest.raises(ValueError, match=r"BUTTON_\* constants"):
        pybadge.is_pressed("start")


def test_rgb_led_accepts_names_and_rgb_tuples(badge_backend):
    pybadge.set_rgb_led("BLUE")
    assert badge_backend.rgb_led == "blue"

    pybadge.set_rgb_led((12, 34, 56))
    assert badge_backend.rgb_led == (12, 34, 56)

    pybadge.turn_rgb_led_off()
    assert badge_backend.rgb_led == pybadge.OFF


def test_addressable_led_strip_pixel_frame_and_clear(badge_backend):
    pybadge.set_led_strip_pixel(3, "red")
    assert badge_backend.led_strip[3] == "red"

    frame = ["off"] * 24
    frame[7] = (10, 20, 30)
    pybadge.set_led_strip(frame)
    assert badge_backend.led_strip == frame

    pybadge.clear_led_strip()
    assert badge_backend.led_strip == [pybadge.OFF] * 24


@pytest.mark.parametrize("index", [-1, 24])
def test_addressable_led_strip_rejects_out_of_range_index(badge_backend, index):
    with pytest.raises(ValueError, match="from 0 to 23"):
        pybadge.set_led_strip_pixel(index, "red")


def test_buzzer_records_and_stops_tone(badge_backend):
    pybadge.play_tone(440, 250)

    assert badge_backend.tones == [(440, 250)]
    assert badge_backend.active_tone == (440, 250)

    pybadge.stop_tone()
    assert badge_backend.active_tone is None


def test_buzzer_rejects_invalid_tone_values(badge_backend):
    with pytest.raises(ValueError, match="greater than zero"):
        pybadge.play_tone(0, 100)
    with pytest.raises(ValueError, match="must not be negative"):
        pybadge.play_tone(440, -1)


def test_display_operations_are_inspectable(badge_backend):
    pybadge.display_clear(pybadge.BLUE)
    pybadge.display_text("Hello", x=12, y=24, color=(255, 255, 0))
    pybadge.display_image("logo.bmp", x=2, y=3)

    assert badge_backend.display_color == pybadge.BLUE
    assert badge_backend.display_operations == [
        ("clear", pybadge.BLUE),
        ("text", "Hello", 12, 24, (255, 255, 0)),
        ("image", "logo.bmp", 2, 3),
    ]


def test_display_rejects_unknown_color(badge_backend):
    with pytest.raises(ValueError, match="unknown color name"):
        pybadge.display_clear("navy")


def test_wifi_results_are_simple_by_default_and_detailed_on_request(badge_backend):
    badge_backend.set_wifi_results(
        [
            {
                "ssid": "ExampleNet",
                "signal_dbm": -42,
                "channel": 6,
                "security": "WPA2",
            }
        ]
    )

    assert pybadge.scan_wifi() == [("ExampleNet", -42)]
    assert pybadge.scan_wifi(include_details=True) == [
        {
            "ssid": "ExampleNet",
            "signal_dbm": -42,
            "channel": 6,
            "security": "WPA2",
        }
    ]


def test_accelerometer_returns_g_values_and_can_be_unavailable(badge_backend):
    badge_backend.set_accelerometer(0.15, -0.25, 0.97)
    assert pybadge.read_accelerometer() == (0.15, -0.25, 0.97)

    badge_backend.accelerometer_values = None
    assert pybadge.read_accelerometer() is None


def test_battery_voltage_returns_volts_not_a_percentage(badge_backend):
    badge_backend.set_battery_voltage(3.87)
    assert pybadge.read_battery_voltage() == 3.87


def test_shutdown_releases_test_outputs(badge_backend):
    pybadge.set_rgb_led("green")
    pybadge.play_tone(330, 100)

    pybadge.shutdown()

    assert pybadge.current_mode() is None
    assert badge_backend.initialized is False
    assert badge_backend.rgb_led == pybadge.OFF
    assert badge_backend.active_tone is None


def test_test_context_manager_shuts_down_after_use():
    from testing import session

    with session() as backend:
        assert pybadge.current_mode() == "test"
        assert backend.initialized

    assert pybadge.current_mode() is None
    assert backend.initialized is False
