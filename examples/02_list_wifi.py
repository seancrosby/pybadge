"""Scan for nearby Wi-Fi networks and show their names and signal strength.

Run from the repository root after `pybadge.py` is implemented. A scan may take
several seconds. The badge does not need to connect to any listed network.
"""

import pybadge


def main():
    pybadge.initialize()
    pybadge.display_clear()
    pybadge.display_text("Scanning for Wi-Fi...", x=8, y=8)

    networks = pybadge.scan_wifi()
    pybadge.display_clear()
    pybadge.display_text("Nearby Wi-Fi networks", x=8, y=8)

    if not networks:
        pybadge.display_text("No networks found", x=8, y=32)
        print("No Wi-Fi networks found.")
        return

    for index, (name, signal_dbm) in enumerate(networks[:9]):
        line = "{} ({:+} dBm)".format(name or "(hidden)", signal_dbm)
        pybadge.display_text(line, x=8, y=32 + index * 20)
        print(line)

    if len(networks) > 9:
        pybadge.display_text("+{} more".format(len(networks) - 9), x=8, y=212)


if __name__ == "__main__":
    main()
