# Echo lines on UART0 (USB-UART). Open the serial monitor at 115200.
import sys
print("Type a line and press Enter")
while True:
    line = sys.stdin.readline()
    if line:
        print("echo:", line.strip())
