# BYU-I e-Badge Board v4.1 — Hardware Reference for Software

This document describes the **BYU-I e-Badge v4.1** custom board (latest iteration **4.1.1**). All pin numbers below are **ESP32-S3 GPIO numbers** unless noted otherwise.

v4.1 keeps the v4.0 GPIO map and adds **USB Host** on the native USB-C port (`USB-CDC-DRD`) plus a three-source power system: **USB (5 V)**, **Vbat (2.8–4.2 V)**, and **Vin (2.8–13 V)**.

---

## Board overview

| Item | Detail |
|------|--------|
| MCU | ESP32-S3-MINI-1-N4R2 (4 MB flash, 2 MB PSRAM) |
| Framework | Arduino (C/C++) with Arduino-ESP32 core |
| USB | Two USB-C ports: **USB-UART** (CP2102N bridge) and **USB-CDC-DRD** (ESP32-S3 native USB, dual-role / USB Host) |
| Display | ST7789 TFT, 240×320 pixels, **SPI2** |
| Input | 6 digital buttons, analog 2-axis joystick |
| LEDs | 1× single-color LED, 1× RGB LED (RS-3535MWAM), 24× WS2812-compatible addressable LEDs (ring) |
| Audio | Piezo buzzer MLT-5020 |
| Motion | MMA8452Q accelerometer on I2C |
| Power | Three sources — USB 5 V, Vbat 2.8–4.2 V (LiPo, TP4056 charger), Vin 2.8–13 V; TPS2121 mux → `PWR_RAW`; `VMain` sense via R41/R44 divider to GPIO 12 (jumper required) |
| Storage | microSD slot (TF push socket), **SPI3** |
| Wireless | WiFi and BLE (built into ESP32-S3) |
| Expansion | GPIO header (`IO<number>`); silkscreen-labeled pads (jumper required); general-purpose **IO13–IO18**; MiniBadge slots; JST connectors |
| Serial | UART0 (USB-UART, GPIO 43/44); UART1 (GPIO 35/36) |
| I2C | GPIO 41 (SDA), GPIO 42 (SCL) — onboard accelerometer and exposed header |

---

## Arduino IDE setup

Do steps **1–3 once** on each computer. For every sketch, start at **step 4**.

### 1. Install the IDE

1. Download the Arduino IDE from [https://www.arduino.cc/en/software](https://www.arduino.cc/en/software).
2. Install it and open the Arduino IDE.

Arduino IDE 2.x is recommended.

### 2. Install the esp32 board package

1. Open **Tools → Board → Boards Manager**.
2. Search for **`esp32`**.
3. Install **esp32** by **Espressif Systems**.

SPI, Wire, WiFi, BLE, Stepper, and SD are included in this core — no separate install needed for those.

### 3. Select the board

**Tools → Board → esp32 → ESP32S3 Dev Module**

For standard use (USB-UART), also set:

- **Tools → USB CDC On Boot → Disabled**
- **Tools → USB Mode → Hardware CDC and JTAG**
- **Tools → Upload Mode → UART0 / Hardware CDC**

These same Tools settings are required for **USB Host**. Only enable **USB CDC On Boot** if you are using the **USB-CDC-DRD** port as a USB device instead (see step 7).

### 4. Select, open, or create a sketch

A *sketch* is an Arduino program (the `.ino` file and its folder).

- **Open a demo:** **File → Open…** and choose a folder under `software/arduino_IDE_example_code/code_for_board_v4_1` (for example `USB-keyboard-demo` or `BatteryMonitor_v4_1`). The folder name must match the `.ino` file name.
- **Create a new sketch:** **File → New Sketch**.
- **Open a recent sketch:** **File → Open Recent**.

### 5. Install any required libraries for that sketch

Open **Sketch → Include Library → Manage Libraries…** (or **Tools → Manage Libraries…**). Search for each library the sketch needs, click **Install**, and choose **Install all** if the IDE asks to add dependencies (for example **Adafruit BusIO**).

| Search for | Install | Used by |
|------------|---------|---------|
| `Adafruit GFX Library` | **Adafruit GFX Library** by Adafruit | TFT in `BatteryMonitor_v4_1`, USB keyboard/mouse demos, and every screen sketch |
| `ST7789` | **Adafruit ST7735 and ST7789 Library** by Adafruit | Same TFT sketches (install GFX first) |
| `FastLED` | **FastLED** by Daniel Garcia | `BatteryMonitor_v4_1`, addressable LED / RGB ring demos |
| `EspUsbHost` | **EspUsbHost** | `USB-keyboard-demo`, `USB-mouse-demo` |
| `ESP32Servo` | **ESP32Servo** by Kevin Harrington, John K. Bennett | Servo and motors demos |
| `MMA8453_n0m1` | **MMA8453_n0m1** by n0m1 | Optional; used by the demo-programs launcher if you run the accelerometer via that library |

Skip any library a given sketch does not use. `BatteryMonitor_v4_1` also uses **WiFi** and **BLEDevice** from the esp32 board package. USB Host sketches pull in TinyUSB through EspUsbHost — accept that dependency if Library Manager offers it.

### 6. Verify (compile) the code

Click the **Verify** checkmark, or **Sketch → Verify/Compile**.

Fix any errors before uploading. Missing libraries show up here as “No such file or directory” for a header such as `Adafruit_ST7789.h` — go back to step 5.

### 7. Connect the board via USB

Plug a USB-C cable into the **USB-UART** port (silkscreen `USB-UART`). That is the standard port for upload and Serial Monitor.

The badge has a second USB-C port, **USB-CDC-DRD**. Pick **one** programming path and pair it with **USB CDC On Boot**:

| Upload port | Silkscreen | CDC On Boot | When to use |
|-------------|------------|-------------|-------------|
| **USB-UART** | `USB-UART` | **Disabled** | Default. CP2102N USB-UART bridge (GPIO 43/44). `Serial` talks to the PC on this path. **Required for USB Host** (CDC-DRD is then free to act as host). |
| **USB-CDC** | `USB-CDC-DRD` | **Enabled** | ESP32-S3 native USB as a **device**. `Serial` maps to on-chip USB-CDC instead of UART0. Do **not** use this while running USB Host. |

For USB Host, keep USB-UART connected to the computer. Power the badge from USB-UART, Vbat, or Vin so `5V_stable` is up — CDC-DRD will **source** VBUS to the attached device and cannot be the badge’s only power input at the same time.

### 8. Power on the board

Flip the power switch to **ON** (silkscreen `ON` / `OFF`). The board must be powered before the COM port appears and before an upload will succeed.

### 9. Select the COM port

**Tools → Port** and choose the COM port that appeared after you connected **USB-UART** and powered the board on.

If no port is listed, check the cable, the USB-UART connector (not CDC-DRD, unless you intentionally enabled CDC), and that the power switch is **ON**.

### 10. Upload the code

Click the **Upload** arrow, or **Sketch → Upload**.

Wait until the IDE reports a successful upload. If upload fails, confirm steps 3, 7, 8, and 9 (board, USB-UART, power ON, matching COM port and CDC setting).

### 11. Reset the board if the program does not start

If the upload finishes but the program does not run, press the **RESET** button on the badge.

Then open **Tools → Serial Monitor** if the sketch prints to `Serial` (115200 baud is typical).

---

## Pin naming: silkscreen labels vs GPIO

The badge PCB has **silkscreen-labeled pads** and a matching **GPIO header** (`IO<number>`). Each silkscreen signal reaches a GPIO pin **only when a jumper wire connects that silkscreen pad to the corresponding `IO<number>` header pin**. No jumper means no electrical connection, even though the names pair up in the table below.

**Use the GPIO number in code** (`const int PIN_A = 34;`), not the silkscreen name.

| Silkscreen | GPIO | Device |
|------------|------|--------|
| `LED` | IO6 | Single-color (onboard) LED |
| `RGBR` | IO2 | RGB LED — red channel |
| `RGBG` | IO4 | RGB LED — green channel |
| `RGBB` | IO5 | RGB LED — blue channel |
| `ALED` | IO7 | Addressable LED data |
| `JSX` | IO8 | Joystick X axis (analog) |
| `JSY` | IO9 | Joystick Y axis (analog) |
| `BtnR` | IO10 | Right button |
| `BtnU` | IO11 | Up button |
| `BtnL` | IO21 | Left button |
| `BtnD` | IO47 | Down button |
| `BtnB` | IO33 | B button |
| `BtnA` | IO34 | A button |
| `BZR` | IO48 | Buzzer |
| `VMain` | IO12 | Board input voltage (`PWR_RAW` through onboard divider). Was `Bt_V` on v4.0. |

Devices wired permanently on the PCB (no silkscreen jumper needed): **display (SPI2)**, **SD card (SPI3)**, **UART0 (GPIO 43/44, CP2102N USB-UART bridge)**, **accelerometer (I2C on GPIO 41/42)**, **native USB (USB-CDC-DRD)**.

---

## Complete GPIO pin map

### User I/O

| GPIO | Name / role | Type | Notes |
|------|-------------|------|-------|
| 2 | RGB red | PWM output | `analogWrite` 0–255 or `digitalWrite` HIGH/LOW |
| 4 | RGB green | PWM output | same |
| 5 | RGB blue | PWM output | same |
| 6 | Single LED | Digital output | HIGH = on, LOW = off |
| 7 | Addressable LEDs | Digital data | WS2812 one-wire data |
| 8 | Joystick X | Analog input | 12-bit ADC, ~0–4095, center ~2048 |
| 9 | Joystick Y | Analog input | same |
| 10 | Button Right | Digital input | HIGH = pressed |
| 11 | Button Up | Digital input | HIGH = pressed |
| 21 | Button Left | Digital input | HIGH = pressed |
| 47 | Button Down | Digital input | HIGH = pressed |
| 33 | Button B | Digital input | HIGH = pressed |
| 34 | Button A | Digital input | HIGH = pressed |
| 48 | Buzzer | PWM / tone | `tone(pin, freq)` and `noTone(pin)` |

### Display (SPI2 / ST7789)

| GPIO | SPI2 signal |
|------|-------------|
| 0 | CS |
| 1 | RST |
| 3 | MOSI |
| 45 | DC (data/command) |
| 46 | SCLK |

MISO is not used for the display. Initialize SPI2 as:

```cpp
SPI.begin(46, -1, 3);  // SCLK, MISO (unused), MOSI
```

### SD card and SPI3

The onboard **microSD slot** uses **SPI3** (separate from the display on SPI2).

| GPIO | SPI3 signal | SD card | Exposed on header |
|------|-------------|---------|-------------------|
| 37 | MISO | yes | yes |
| 38 | CLK (SCLK) | yes | yes |
| 39 | MOSI | yes | yes |
| 40 | CS | yes (onboard SD only) | **no** |

SPI3 **CLK, MISO, and MOSI** (GPIO 38, 37, 39) are broken out on the GPIO header for external SPI devices. **CS (GPIO 40) is not exposed** — it is dedicated to the onboard SD card.

An external SPI peripheral can share the SPI3 bus with the SD slot, but it must use a **separate chip-select on any free available GPIO** (for example IO13–IO18). Only one device is active on the bus at a time; drive each CS pin high when idle, and low only when talking to that device.

```cpp
// Onboard microSD on SPI3
const int PIN_SD_CS   = 40;
const int PIN_SPI3_MISO = 37;
const int PIN_SPI3_MOSI = 39;
const int PIN_SPI3_SCLK = 38;

// Example: external SPI device CS on a free GPIO
const int PIN_EXT_SPI_CS = 13;

SPIClass spi3(HSPI);  // or the ESP32-S3 SPI instance mapped to SPI3 in your core

void setup() {
  pinMode(PIN_SD_CS, OUTPUT);
  pinMode(PIN_EXT_SPI_CS, OUTPUT);
  digitalWrite(PIN_SD_CS, HIGH);      // SD idle (deselected)
  digitalWrite(PIN_EXT_SPI_CS, HIGH); // external device idle

  spi3.begin(PIN_SPI3_SCLK, PIN_SPI3_MISO, PIN_SPI3_MOSI, PIN_SD_CS);
}
```

Do not use GPIO 40 as CS for an external device — it is wired to the onboard SD card.

### I2C

| GPIO | I2C signal | Notes |
|------|------------|-------|
| 41 | SDA | Exposed on GPIO header; shared with onboard accelerometer |
| 42 | SCL | Exposed on GPIO header; shared with onboard accelerometer |

Onboard device: **MMA8452Q** accelerometer at address **`0x1C`**. Register `0x0D` (WHO_AM_I) should read **`0x2A`**.

```cpp
#include <Wire.h>
Wire.setPins(41, 42);  // SDA, SCL
Wire.begin();
```

### Board input voltage sense (`VMain` → IO12)

| GPIO | Role |
|------|------|
| 12 | Analog input — scaled `PWR_RAW` from the onboard divider |

Jumper **`VMain` → `IO12`** to read the voltage of whichever source the power mux has selected (USB, Vbat, or Vin). The divider is on the PCB between `PWR_RAW` and this sense line:

```
PWR_RAW ── R41 (150 kΩ) ── VMain / GPIO 12 ── R44 (10 kΩ) ── GND
```

| Resistor | Value | Role |
|----------|-------|------|
| R41 | **150 kΩ** | Top leg (`PWR_RAW` to sense node) |
| R44 | **10 kΩ** | Bottom leg (sense node to GND) |

At the sense node (GPIO 12 when jumped):

- V_sense = V_pwr × 10 / (150 + 10) = V_pwr × **10/160** = V_pwr × **1/16**
- V_pwr = V_sense × **16**

The 16:1 divider maps a 16 V rail to 1.0 V at the pin, which fits the ESP32-S3 **0 dB** ADC range (~1.1 V full-scale). The board is rated **13 V** on Vin (silkscreen and SMAJ13CA TVS), so the pin stays at 13 × 1/16 = **0.8125 V**.

See **Power supplies and voltage sense** below for ADC settings and conversion code.

### UART0 — USB serial

GPIO 43 and 44 are **fixed on the PCB** to the CP2102N USB-UART bridge — not silkscreen-jumpable. This is the **USB-UART** port.

| GPIO | UART0 signal | Notes |
|------|--------------|-------|
| 43 | TX | Connected to CP2102N USB-UART bridge |
| 44 | RX | Connected to CP2102N USB-UART bridge |

In Arduino, UART0 is `Serial` (USB programming and Serial Monitor) when **USB CDC On Boot** is **Disabled**.

```cpp
Serial.begin(115200);
```

### UART1 — exposed serial

| GPIO | UART1 signal | Notes |
|------|--------------|-------|
| 35 | TX | Available on GPIO header |
| 36 | RX | Available on GPIO header |

In Arduino, use `Serial1`:

```cpp
Serial1.begin(115200, SERIAL_8N1, 36, 35);  // RX, TX
Serial1.println("hello");
```

Settings: typically **115200**, 8N1.

### General-purpose GPIO (IO13–IO18)

GPIO **13, 14, 15, 16, 17, and 18** are broken out on the GPIO header as **IO13** through **IO18**. They are **general-purpose** and available for external circuits (servo, motors, sensors, etc.) whenever they are **not** in use by a MiniBadge.

These same pins can be **jumpered to a MiniBadge** expansion board. If no MiniBadge is connected (or those lines are not jumpered to it), the pins are free for any other purpose.

```cpp
const int PIN_GP_13 = 13;
const int PIN_GP_14 = 14;
const int PIN_GP_15 = 15;
const int PIN_GP_16 = 16;
const int PIN_GP_17 = 17;
const int PIN_GP_18 = 18;

void setup() {
  pinMode(PIN_GP_13, OUTPUT);
  digitalWrite(PIN_GP_13, HIGH);
}
```

| GPIO | Header | MiniBadge routing (when jumped) |
|------|--------|--------------------------------|
| 13 | IO13 | Slot A — CLK |
| 14 | IO14 | Slot A |
| 15 | IO15 | Slot A |
| 16 | IO16 | Slot B — CLK |
| 17 | IO17 | Slot B |
| 18 | IO18 | Slot B |

Use each pin for **one** function at a time: either general-purpose I/O on the header, or MiniBadge (via jumper), not both.

### Other expansion notes

| GPIO | Notes |
|------|-------|
| 12 | Board voltage sense (`VMain` → IO12) — do not repurpose while monitoring `PWR_RAW` |

---

## Input behavior

### Buttons

- Wired with **external pull-down** resistors.
- **Pressed = `HIGH`**, released = `LOW`.
- Use `pinMode(pin, INPUT)` (no `INPUT_PULLUP`).

```cpp
const int PIN_A = 34;

bool isPressed(int pin) {
  return digitalRead(pin) == HIGH;
}

void setup() {
  pinMode(PIN_A, INPUT);
}
```

### Joystick

- **Analog** on GPIO 8 (X) and GPIO 9 (Y).
- ESP32-S3 ADC is **12-bit**: raw values about **0–4095**.
- Center (stick released) is about **2048**.
- A useful “pushed” threshold is **±600** from 2048.

```cpp
const int PIN_JOYSTICK_X = 8;
const int PIN_JOYSTICK_Y = 9;

int vx = analogRead(PIN_JOYSTICK_X);
int vy = analogRead(PIN_JOYSTICK_Y);
```

---

## Outputs

### Single-color LED (GPIO 6)

```cpp
const int PIN_LED = 6;

void setup() {
  pinMode(PIN_LED, OUTPUT);
}

void loop() {
  digitalWrite(PIN_LED, HIGH);  // on
  delay(500);
  digitalWrite(PIN_LED, LOW);   // off
  delay(500);
}
```

Silkscreen jumper: **`LED` → `IO6`**.

### RGB LED (GPIO 2, 4, 5)

**On/off per channel** — pure red, green, or blue:

```cpp
const int PIN_RED   = 2;
const int PIN_GREEN = 4;
const int PIN_BLUE  = 5;

void setup() {
  pinMode(PIN_RED,   OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_BLUE,  OUTPUT);
}

digitalWrite(PIN_RED,   HIGH);
digitalWrite(PIN_GREEN, LOW);
digitalWrite(PIN_BLUE,  LOW);   // red only
```

**PWM brightness** — color mixing with values 0–255:

```cpp
void setRgbColor(int r, int g, int b) {
  analogWrite(PIN_RED,   r);
  analogWrite(PIN_GREEN, g);
  analogWrite(PIN_BLUE,  b);
}
```

Silkscreen jumpers: **`RGBR`→`IO2`**, **`RGBG`→`IO4`**, **`RGBB`→`IO5`**.

### Addressable LED ring (GPIO 7)

| Parameter | Value |
|-----------|--------|
| Count | **24** LEDs |
| Type | WS2812-compatible (SK6805) |
| Color order | **GRB** |
| Arduino library | FastLED |

```cpp
#include <FastLED.h>

const int PIN_ADDR_LEDS = 7;
const int NUM_LEDS = 24;
CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<WS2812, PIN_ADDR_LEDS, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(50);
  FastLED.clear();
  FastLED.show();
}
```

Silkscreen jumper: **`ALED` → `IO7`**.

### Buzzer (GPIO 48)

```cpp
const int PIN_BUZZER = 48;

void setup() {
  pinMode(PIN_BUZZER, OUTPUT);
}

void loop() {
  tone(PIN_BUZZER, 523);
  delay(200);
  noTone(PIN_BUZZER);
}
```

Silkscreen jumper: **`BZR` → `IO48`**.

### Servo motor (external, e.g. GPIO 13)

Arduino library: **ESP32Servo**.

Wiring:
- Red → 5V
- Brown → GND
- Orange (signal) → any free general-purpose pin (e.g. **IO13**)

```cpp
#include <ESP32Servo.h>

const int PIN_SERVO = 13;
Servo myServo;

void setup() {
  myServo.attach(PIN_SERVO);
}

void loop() {
  myServo.write(90);  // angle 0–180
}
```

GPIO 13 is a general-purpose header pin (IO13). It can be jumpered to MiniBadge slot A instead — use it for one purpose or the other, not both.

---

## TFT display (ST7789)

| Parameter | Value |
|-----------|--------|
| Native resolution | 240×320 (portrait) |
| Landscape use | 320×240 after `setRotation(1)` |
| Color order | BGR |

### Init

```cpp
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>

#define TFT_CS   0
#define TFT_RST  1
#define TFT_DC   45
#define TFT_MOSI 3
#define TFT_SCLK 46

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

void setup() {
  SPI.begin(TFT_SCLK, -1, TFT_MOSI);
  tft.init(240, 320);
  tft.setRotation(1);           // landscape: 320 wide, 240 tall
  tft.fillScreen(ST77XX_BLACK);
  tft.setTextSize(2);
  tft.setTextColor(ST77XX_WHITE);
  tft.setCursor(0, 0);
}
```

### Drawing and text

```cpp
tft.fillScreen(ST77XX_BLUE);
tft.drawPixel(100, 50, ST77XX_WHITE);
tft.fillRect(10, 10, 100, 40, ST77XX_RED);
tft.println("Hello");
tft.printf("Integer: %d\n", 42);
tft.printf("Float: %.2f\n", 3.14);
tft.printf("String: %s\n", "e-Badge");
```

| Printf specifier | Type |
|------------------|------|
| `%d` | integer |
| `%f` / `%.1f` / `%.2f` | floating point |
| `%s` | C string (`const char*`) |
| `%c` | single character |
| `\n` | new line |

- `tft.setTextWrap(false)` — disable automatic line wrapping
- `tft.cp437(true)` — CP437 glyphs (arrows: `\x18` `\x19` `\x1A` `\x1B`)

### Built-in color constants

`ST77XX_BLACK`, `ST77XX_WHITE`, `ST77XX_RED`, `ST77XX_GREEN`, `ST77XX_BLUE`, `ST77XX_YELLOW`, `ST77XX_CYAN`, `ST77XX_MAGENTA`

Custom RGB565 colors: `uint16_t c = tft.color565(255, 128, 0);`

### Text size vs line width (landscape, rotation 1)

Default font: **6×8 px per character at `setTextSize(1)`**.

| `setTextSize` | Char size (px) | ~Max chars per row (320 px) |
|---------------|----------------|-----------------------------|
| 1 | 6 × 8 | ~53 |
| 2 | 12 × 16 | ~26 |
| 3 | 18 × 24 | ~17 |
| 4 | 24 × 32 | ~13 |

---

## Accelerometer (MMA8452Q)

| Item | Value |
|------|--------|
| Chip | MMA8452Q (MMA8451 also possible; WHO_AM_I `0x1A`) |
| Bus | I2C on GPIO 41 (SDA), GPIO 42 (SCL) |
| I2C address | `0x1C` |
| WHO_AM_I register | `0x0D` → expect `0x2A` for MMA8452Q |

```cpp
#include <Wire.h>

const int PIN_I2C_SDA = 41;
const int PIN_I2C_SCL = 42;
const uint8_t ACCEL_ADDR = 0x1C;

void setup() {
  Wire.setPins(PIN_I2C_SDA, PIN_I2C_SCL);
  Wire.begin();

  // ±2g range (register 0x0E = 0x00), active mode (0x2A = 0x01)
  Wire.beginTransmission(ACCEL_ADDR);
  Wire.write(0x0E); Wire.write(0x00);
  Wire.endTransmission();
  Wire.beginTransmission(ACCEL_ADDR);
  Wire.write(0x2A); Wire.write(0x01);
  Wire.endTransmission();
}
```

Read 6 bytes starting at register `0x01` (X, Y, Z MSB/LSB pairs). In ±2g mode, divide the 14-bit signed value by **1024** to get acceleration in **g**.

Capabilities: raw X/Y/Z in g, orientation (portrait/landscape), tap/double-tap, shake, free-fall.

### Interrupt pins (INT1, INT2)

The MMA8452Q **INT1** and **INT2** outputs are routed to a **2-pin header near the accelerometer (header U18)** on the PCB. These pads are **not silkscreen-labeled**. To use hardware interrupts, jumper each interrupt line from header U18 to a free **GPIO header pin** (`IO<number>`), then configure that GPIO as an input and attach an interrupt handler in software. I2C polling works without these jumpers.

Optional Arduino library: **MMA8453_n0m1**.

---

## Power supplies and voltage sense

v4.1 accepts **three** power sources. Onboard management (TPS2121 power mux, TP4056 LiPo charger, TPS630701 buck-boost to `5V_stable`, AP63201 3.3 V buck) picks a source and produces the rails the rest of the board uses.

### Sources

| Source | Silkscreen | Range | Notes |
|--------|------------|-------|-------|
| **USB** | `USB-UART`, `USB-CDC-DRD` | **5 V** | Either USB-C port can **sink** 5 V when a host/charger is attached. USB-UART is the usual programming/power port. USB-CDC-DRD can instead **source** 5 V when acting as USB Host. |
| **Vbat** | `VBAT 2.8-4.2V` | **2.8–4.2 V** | 1S LiPo / Li-ion. Charged by the onboard TP4056 from USB 5 V. `CHG` LED indicates charging. |
| **Vin** | `VIN 2.8-13V` | **2.8–13 V** | External supply on the Vin connector. Protected by an SMAJ13CA TVS; do not exceed **13 V**. |

The mux output is **`PWR_RAW`**. GPIO 12 (when jumped to `VMain`) measures `PWR_RAW`, not a dedicated battery-only node — the reading is whichever source is currently selected (typically ~5 V on USB, 2.8–4.2 V on battery alone, or the Vin voltage when Vin is selected).

`5V_stable` is generated from `PWR_RAW` and is what USB Host uses to source VBUS. Power the badge from USB-UART, Vbat, or Vin before plugging a device into USB-CDC-DRD.

### Hardware (sense circuit)

Read `PWR_RAW` on **GPIO 12** after jumping **`VMain` → `IO12`**.

| Item | Value |
|------|--------|
| Silkscreen / sense pad | **`VMain`** (jumper to **IO12**) |
| Sense pin | **GPIO 12** (analog input) |
| Divider | **R41 = 150 kΩ** (`PWR_RAW` → sense), **R44 = 10 kΩ** (sense → GND) |
| ADC resolution | 12-bit (0–4095) |
| ADC attenuation | **0 dB** (~1.1 V full-scale nominal) |
| Divider formula | V_sense = V_pwr × 10 / (150 + 10) = V_pwr × **1/16** |
| Inverse | V_pwr = V_sense × **16** |
| Max Vin (rated) | **13.0 V** |
| Pin voltage at 13 V | 13 × (1/16) = **0.8125 V** (within 0 dB range) |
| Pin voltage at 16 V (divider design) | 16 × (1/16) = **1.0 V** |

v4.0 used a 150 kΩ / 47 kΩ divider and **6 dB** attenuation for a battery-only sense line (`Bt_V`). Do not reuse v4.0 conversion constants on v4.1.

### Voltage conversion

```cpp
const int PIN_PWR_SENSE    = 12;
const int   ADC_MAX        = 4095;
const float ADC_FULL_SCALE = 1.1f;            // volts at ADC pin when raw = 4095 (0 dB; calibrate per chip)
const float DIVIDER_RATIO  = 160.0f / 10.0f;  // (150k + 10k) / 10k = 16

void setup() {
  pinMode(PIN_PWR_SENSE, INPUT);
  analogSetAttenuation(ADC_0db);
}

float readPwrRawVoltage() {
  int raw = analogRead(PIN_PWR_SENSE);
  float vAdc = (raw / (float)ADC_MAX) * ADC_FULL_SCALE;
  float vPwr = vAdc * DIVIDER_RATIO;
  return vPwr;
}
```

`ADC_FULL_SCALE` should be calibrated per chip: apply a known voltage at Vin (or measure Vbat at the connector), compare to the computed value, and adjust `ADC_FULL_SCALE` until they agree.

Example sketch: `software/arduino_IDE_example_code/code_for_board_v4_1/BatteryMonitor_v4_1`.

### Reference voltage levels

| Voltage | Meaning |
|---------|---------|
| 2.8 V | Minimum Vbat / Vin |
| 4.2 V | Fully charged 1S LiPo |
| 5.0 V | Typical USB 5 V |
| 13.0 V | Maximum Vin (board rating) |

Raw ADC alone is not a percent-charge indicator — convert to volts using the divider ratio above, and remember the reading tracks **`PWR_RAW`**, which may be USB or Vin rather than the cell.

---

## Serial communication

### UART0 (USB-UART) — `Serial`

GPIO 43 and 44 are **fixed on the PCB** to the CP2102N USB-UART bridge (not jumpable). Used for programming and PC communication on the **USB-UART** port.

| GPIO | Signal |
|------|--------|
| 43 | TX |
| 44 | RX |

```cpp
void setup() {
  Serial.begin(115200);
  delay(2000);  // allow host to connect after reset
}

void loop() {
  Serial.println("Hello from e-Badge!");
  if (Serial.available() > 0) {
    String text = Serial.readStringUntil('\n');
    text.trim();
    Serial.println(text);
  }
}
```

### UART1 — `Serial1`

Exposed on the GPIO header for wired communication with other devices.

| GPIO | Signal |
|------|--------|
| 35 | TX |
| 36 | RX |

```cpp
void setup() {
  Serial1.begin(115200, SERIAL_8N1, 36, 35);  // RX pin, TX pin
}

void loop() {
  if (Serial1.available() > 0) {
    char c = Serial1.read();
    Serial1.write(c);  // echo
  }
}
```

---

## USB Host (USB-CDC-DRD)

The **USB-CDC-DRD** port is the ESP32-S3 native USB (D+/D− on GPIO 19/20 internally). A TUSB321 CC controller and load switches make the port **dual-role**: it can act as a USB **device** (CDC serial) or as a USB **host** that sources 5 V and enumerates a keyboard, mouse, or other USB device.

Host/source mode is hardware-detected from the USB-C CC pins. The **`USB_PWR_SRC`** LED lights when the port is sourcing VBUS (host/source). By default the port is a **sink**; it sources only when a downstream device (or a true OTG adapter) is recognized.

### Hardware setup

1. Power the badge from **USB-UART**, **Vbat**, or **Vin** so `5V_stable` is up.
2. On **USB-CDC-DRD** use a **true USB-C OTG adapter**: USB-C male (into the badge) → USB-A female (for the keyboard/mouse). Charge-only / non-OTG adapters will not ask the port to source VBUS.
3. Confirm **`USB_PWR_SRC`** is on, then plug in the device.
4. If the device has no power, try another OTG adapter or a **powered USB hub** between the adapter and the device.

Do not use USB-CDC-DRD as the badge’s only power input while hosting — that port is sourcing, not sinking.

### Software

Arduino library: **EspUsbHost** (Library Manager). Example sketches: `software/arduino_IDE_example_code/code_for_board_v4_1/USB-keyboard-demo` and `software/arduino_IDE_example_code/code_for_board_v4_1/USB-mouse-demo`.

Use Arduino IDE setup **steps 3 and 7** (USB-UART, CDC On Boot Disabled). `usb.begin()` fails if CDC-on-boot has claimed the native USB port.

```cpp
#include "EspUsbHost.h"

EspUsbHost usb;

void setup() {
  Serial.begin(115200);  // USB-UART; CDC On Boot must be Disabled

  usb.setKeyboardLayout(ESP_USB_HOST_KEYBOARD_LAYOUT_EN_US);

  usb.onDeviceConnected([](const EspUsbHostDeviceInfo &device) {
    Serial.printf("USB connected: VID=%04X PID=%04X %s\n",
                  device.vid, device.pid, device.product);
  });

  usb.onDeviceDisconnected([](const EspUsbHostDeviceInfo &device) {
    Serial.printf("USB disconnected: VID=%04X PID=%04X\n",
                  device.vid, device.pid);
  });

  usb.onKeyboard([](const EspUsbHostKeyboardEvent &event) {
    if (!event.pressed) return;
    if (event.ascii >= 0x20 && event.ascii != 0x7F) {
      Serial.write((char)event.ascii);
    }
  });

  usb.onMouse([](const EspUsbHostMouseEvent &event) {
    Serial.printf("mouse dx=%d dy=%d buttons=0x%02X\n",
                  event.x, event.y, event.buttons);
  });

  if (!usb.begin()) {
    Serial.printf("usb.begin() failed: %s\n", usb.lastErrorName());
  }
}

void loop() {
  delay(1);  // USB work runs in EspUsbHost's background task
}
```

USB Host and USB-CDC device mode cannot share the native port at the same time. Keep **CDC On Boot Disabled** and use **USB-UART** for `Serial`.

---

## WiFi and BLE

Built into the ESP32-S3; no dedicated GPIO pins.

```cpp
#include <WiFi.h>
WiFi.mode(WIFI_STA);
int n = WiFi.scanNetworks();
```

---

## Required libraries

Install steps and Library Manager search names are in **Arduino IDE setup, step 5**.

| Feature | Library |
|---------|---------|
| TFT display | Adafruit GFX Library, Adafruit ST7735 and ST7789 Library (Adafruit BusIO as a dependency) |
| Addressable LEDs | FastLED |
| Accelerometer (optional) | MMA8453_n0m1 |
| Servo | ESP32Servo |
| Stepper motor | Stepper (built into Arduino) |
| WiFi / BLE | WiFi, BLEDevice (ESP32 Arduino core) |
| SD card | SD (built into Arduino) or SD_MMC |
| USB Host | EspUsbHost |

SPI and Wire are included with the Arduino-ESP32 core. See **Arduino IDE setup** above for board package, library install, and target selection.

---

## Hardware smoke-test checklist

| Test | GPIO / bus | Quick action |
|------|------------|--------------|
| Single LED | 6 | `digitalWrite` toggle |
| RGB | 2, 4, 5 | one channel `HIGH` |
| Ring LED | 7 | FastLED: `leds[0] = red`, `show()` |
| Button A | 34 | `digitalRead` → HIGH when pressed |
| Joystick | 8, 9 | `analogRead` → ~2048 at center |
| Buzzer | 48 | `tone(523)` then `noTone` |
| TFT display | SPI 0,1,3,45,46 | `fillScreen`, `println` |
| SD card | SPI3: 37,38,39,40 | SD library init on SPI3, CS=40 |
| Accelerometer | I2C 41,42 @ 0x1C | read register 0x0D → 0x2A |
| Board voltage | 12 | Jumper `VMain`→`IO12`, `analogRead` with `ADC_0db`, ×16 |
| USB serial | UART0 / `Serial` | `Serial.println("ok")` on USB-UART |
| Header serial | UART1 / `Serial1` | `Serial1.println("ok")` on GPIO 35/36 |
| USB Host | USB-CDC-DRD | Keyboard/mouse demo; `USB_PWR_SRC` LED on with OTG adapter |

---

## Quick pin reference

Everything on the list below can be **jumped** to its adjacent onboard device (via the silkscreen-labeled pad) **or left unjumped** and used as a general-purpose GPIO on that `IO<number>` header pin. Pins 13–18 are the **MiniBadge** pins. Display (SPI2), UART0 (GPIO 43/44), native USB, and SD card CS (GPIO 40) are not on this list — they are fixed on the PCB.

```cpp
// BYU-I e-Badge v4.1
const int PIN_JOYSTICK_X = 8;
const int PIN_JOYSTICK_Y = 9;
const int PIN_RIGHT  = 10;
const int PIN_UP     = 11;
const int PIN_LEFT   = 21;
const int PIN_DOWN   = 47;
const int PIN_B      = 33;
const int PIN_A      = 34;
const int PIN_RED    = 2;
const int PIN_GREEN  = 4;
const int PIN_BLUE   = 5;
const int PIN_LED    = 6;
const int PIN_ADDR_LEDS = 7;
const int PIN_BUZZER = 48;
const int PIN_I2C_SDA = 41;
const int PIN_I2C_SCL = 42;
const int PIN_PWR_SENSE = 12;  // jumper VMain → IO12; reads PWR_RAW
const int PIN_UART1_TX = 35;
const int PIN_UART1_RX = 36;
// MiniBadge pins (IO13–IO18)
const int PIN_IO13 = 13;
const int PIN_IO14 = 14;
const int PIN_IO15 = 15;
const int PIN_IO16 = 16;
const int PIN_IO17 = 17;
const int PIN_IO18 = 18;
```

Onboard-wired (not jumpable):

```cpp
#define TFT_CS   0
#define TFT_RST  1
#define TFT_DC   45
#define TFT_MOSI 3
#define TFT_SCLK 46

const int PIN_UART0_TX = 43;
const int PIN_UART0_RX = 44;

// SPI3 — SD card; CLK/MISO/MOSI exposed on header, CS 40 onboard only
const int PIN_SD_CS     = 40;
const int PIN_SPI3_MISO = 37;
const int PIN_SPI3_MOSI = 39;
const int PIN_SPI3_SCLK = 38;

const int NUM_LEDS = 24;
const uint8_t ACCEL_ADDR = 0x1C;
```
