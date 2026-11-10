# WiFi + BLE scan demo — e-Badge v4 (learning_Python).
# WiFi: network.WLAN(STA_IF).scan(). BLE: bluetooth.BLE().gap_scan() where the port supports it.

import utime

import network

from board_v4 import (
    DISPLAY_H,
    tft,
    font,
    st7789,
    tft_init,
    is_pressed,
    button_A,
    button_B,
    play_tone,
    tft_clear,
)

tft_init(include_status_bar=False)


def _ssid_str(net):
    ssid = net[0]
    if isinstance(ssid, bytes):
        try:
            s = ssid.decode("utf-8")
        except Exception:
            s = "?"
        return s if s else "(hidden)"
    return str(ssid) if ssid else "(hidden)"


def draw_wifi_page(nets):
    tft.fill(st7789.BLACK)
    tft.text(font, "WiFi scan", 4, 4, st7789.CYAN, st7789.BLACK)
    if not nets:
        tft.text(font, "(none / error)", 4, 28, st7789.YELLOW, st7789.BLACK)
        return
    nets_sorted = sorted(nets, key=lambda n: n[3], reverse=True)
    y = 22
    for net in nets_sorted[:9]:
        name = _ssid_str(net)
        rssi = net[3]
        line = name[:18] + " %d" % rssi
        tft.text(font, line, 4, y, st7789.WHITE, st7789.BLACK)
        y += 14
    if len(nets_sorted) > 9:
        tft.text(font, "+%d more" % (len(nets_sorted) - 9), 4, y, 0x8410, st7789.BLACK)


def draw_ble_page(lines):
    tft.fill(st7789.BLACK)
    tft.text(font, "BLE scan", 4, 4, st7789.MAGENTA, st7789.BLACK)
    y = 22
    for line in lines[:10]:
        tft.text(font, line[:26], 4, y, st7789.WHITE, st7789.BLACK)


def run_wifi_scan():
    wlan = network.WLAN(network.STA_IF)
    try:
        wlan.active(True)
        nets = wlan.scan()
    except Exception as e:
        tft.fill(st7789.BLACK)
        tft.text(font, "WiFi error", 4, 22, st7789.RED, st7789.BLACK)
        tft.text(font, str(e)[:28], 4, 40, st7789.YELLOW, st7789.BLACK)
        sleep(2500)
        return
    draw_wifi_page(nets)
    sleep(2000)


def run_ble_scan():
    lines = []
    try:
        import bluetooth

        ble = bluetooth.BLE()
        ble.active(True)
        seen = {}

        def _irq(ev, data):
            if ev == bluetooth._IRQ_SCAN_RESULT:
                try:
                    addr_type, addr, adv_type, rssi, adv_data = data
                except (ValueError, TypeError):
                    return
                key = bytes(addr)
                prev = seen.get(key, -128)
                if rssi > prev:
                    seen[key] = rssi

        ble.irq(_irq)
        if not hasattr(ble, "gap_scan"):
            mac = ble.config("mac")
            lines = ["gap_scan N/A", "MAC: " + repr(mac)]
        else:
            ble.gap_scan(4000, 30000, 30000, False)
            sleep(4200)
            try:
                ble.gap_scan(None)
            except Exception:
                pass
            for addr, rssi in sorted(seen.items(), key=lambda kv: kv[1], reverse=True)[:24]:
                h = ":".join("%02x" % b for b in addr)
                lines.append("%s %d" % (h, rssi))
            if not lines:
                lines = ["(no advertisers)"]
    except ImportError:
        lines = ["bluetooth module", "not in firmware"]
    except Exception as e:
        lines = ["BLE error:", str(e)[:24]]

    draw_ble_page(lines)
    sleep(2500)


def main():
    tft.fill(st7789.BLACK)
    tft.text(font, "Wireless test", 4, 4, st7789.GREEN, st7789.BLACK)
    tft.text(font, "A: WiFi  B: BLE", 4, 30, st7789.WHITE, st7789.BLACK)
    tft.text(font, "Both: full cycle", 4, 48, st7789.WHITE, st7789.BLACK)
    sleep(1500)

    while True:
        a = is_pressed(button_A)
        b = is_pressed(button_B)
        if a and b:
            play_tone(440, 60)
            run_wifi_scan()
            run_ble_scan()
        elif a:
            play_tone(520, 40)
            run_wifi_scan()
        elif b:
            play_tone(620, 40)
            run_ble_scan()
        else:
            sleep(50)
            continue

        tft.text(font, "A/B/cycle again", 4, DISPLAY_H - 18, st7789.CYAN, st7789.BLACK)
        sleep(400)
        while is_pressed(button_A) or is_pressed(button_B):
            sleep(30)
        tft.fill(st7789.BLACK)
        tft.text(font, "Wireless test", 4, 4, st7789.GREEN, st7789.BLACK)
        tft.text(font, "A: WiFi  B: BLE", 4, 30, st7789.WHITE, st7789.BLACK)
        tft.text(font, "Both: full cycle", 4, 48, st7789.WHITE, st7789.BLACK)


try:
    main()
except Exception as e:
    tft_clear()
    print("Wireless demo error:", e)
    raise
