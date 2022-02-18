# Introduction

Used to scroll text across a WS2812B LED Array.
Particularly useful when scrolling text received over the Internet, which is why this library came into creation. The Arduino library is built on C, which makes working with strings of arbitrary length particularly unpleasant (especially for a C novice like me!). FastLED (the main Arduino library) is the work of a (late) genius, but seems to be more focused on light displays than scrolling text. There is an LEDText library, which is handy, but again, beyond my capabilities to efficiently web integrate this. You can see / try my mostly successful implementation [here](https://github.com/fadesibert/arduino_esp32_scroller)

I ended up going the python route, because the Arduino I was using didn't have enough RAM to get all 96 columns that I wanted to use (undoubtedly due to the hamfistedness of my implementation).

Two ports in this repo:
* parse_led.py - runs on RaspberryPi or an x86 with GPIO. A little power hungry (as it is typically scheduled by cron), you can get ~30h on a 2000mAh battery (or run it from wall power). Can get about 40 refreshes / sec
* esp32_scroll.py - not strictly limited to ESP32 (rather, bounded by any microcontroller that MicroPython can be flashed to, and with enough RAM). A little bit more forethought is required - ScrollDirection, LED_WIDTH and LED_HEIGHT need to be known at compile / flash time - but given that the matrix is generally assembled (physically) once... well... seems like an *OK* tradeoff. #thingsIwillregretsaying

# Platform Notes

__Every platform has its quirks - the two ports in this repo are no different__

## CPython

Best scheduled with cron. Bear in mind that this app will need to run as root (fml), and given the many dependencies in this implementation, best run in an appropriately configured venv as `sudo $(which python) parse_led.py`

## ESP32

The ESP32 runs at 3.3V, but many / most WS2812Bs run off of 5V. You can sometimes just get away with it, but there are a few methods of ensuring success:
* (my current approach) Use a linear voltage regulator such as the LM317T to boost the 3.3V PWM logic to 5V. The [WS2812B datasheet](https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf) specifies minimum 1/0 levels and tolerances - so adjust accordingly. Given that I powered this device from a USB brick, and the fact that the GPIO ports *really* don't like to put out more than 500mA (your requirements will be a function of number of LEDs and brightness) - I used one USB connection to the ESP32 to power the controller and the GPIO logic (and to provide the LV side of the LM317T), and one connection into the high side of the LM317T, and directly into the Vcc / GND connection of the WS2812.
* `machine.Pin(NN, Pin.OUT)` is used to select the connected GPIO pin and pass it to NeoPixel. An LED or an Oscilloscope can help verify if you have the correct pin. The Pinout diagram for the [Feather](https://learn.adafruit.com/assets/41623) for example is pretty good - use the integers on the Pinout. Not all pins can be used for PWM (Pulse Width Modulation, how WS2812B communicates), and not all can be used for output. The ESP32 DevKit [Pinout diagram](https://www.mischianti.org/wp-content/uploads/2020/11/ESP32-DOIT-DEV-KIT-v1-pinout-mischianti.png) (which I also used) is hardeer to read, but again, the `machine.Pin` seems to refer to the Numeric value (green box), which differs from the GPIO Port __sometimes__. 
* There are some hacks with shorting the first pixel so it behaves like a diode, but the wisdom / efficacy of this method is beyond my electrical engineering skills
* Use an SPI based implementation. Left as an exercise to the reader

# Diagrams

__Some crude circuit diagrams for assembling hardware.__
ESP32 -> WS2812B

```mermaid
flowchart LR
    idV[5V]
    idV1[5V]
    idV2[GND]
    idA[ESP32]
    idA1[ESP32 3V3]
    idA2[ESP32 GND]
    idA3[ESP32 GPIO]
    idB[LM317T (High)]
    idC[LM317T (Low)]
    idD[WS2812B]
    idD1[WS VCC]
    idD2[WS DATA]
    idD3[WS GND]
    V --> V1
    V1 --> A & B
    V2 --> D3
    A --> A1 & A2 & A3
    A1 --> C
    C --> B
    B --> D
    A3 --> C
    B --> D1
    B --> D2
    D <-- D1 & D2 & D3

```

# Addendum

Uses font header files - as found in LEDText - to generate binary arrays for mLED Matrix Displays (like WS2812B) - which take simple on/off clocked signals. Useful for using Python (maybe CircuitPy?) for displaying scrolling text on a standard set of LED Stirips
