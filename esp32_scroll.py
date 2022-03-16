import gc
import time
from array import array
from math import floor

#import neopixel
#import network
import uctypes
#from machine import Pin, deepsleep
from micropython import const, mem_info
from ulab import numpy
# hack when running *nix micropython port
const = lambda x: int(x)

LEFT = const(1)
RIGHT = const(-1)
LED_PIN = const(23)  # Modify this value to change LED Pin. Refer to Pinout Diagram
LED_INTERNAL_PIN = const(2)
LED_BRIGHTNESS = const(50)  # value out 100
LED_BRIGHT_MULT = int(floor((LED_BRIGHTNESS / 255)))

LED_WIDTH = const(96)
LED_HEIGHT = const(8)
LED_FIELD = const(LED_WIDTH * LED_HEIGHT)

SCROLL_DIRECTION_LEFT = const(1)
SCROLL_DIRECTION_RIGHT = const(-1)

WIFI_ESSID = "Revmo"
WIFI_KEY = "gr@ph$n0de!"

ENDPOINT_URI = "https://myfancyapi.com/messages/"

TIME_MINS_IN_MILLIS = const(60 * 1000)
SLEEP_TIME = 2 * TIME_MINS_IN_MILLIS

# Using Consts as Enum not supported in MicroPython
SCROLL_DIRECTION = SCROLL_DIRECTION_LEFT  # change this using another const

# Once basic functionality established, switch to memoryview, array or const
FONT_MAP = numpy.array(
    [
        [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
        [0x186A0, 0x186A0, 0x186A0, 0x186A0, 0x186A0, 0x0, 0x186A0],
        [0xF6950, 0xF6950, 0xF6950, 0x0, 0x0, 0x0, 0x0],
        [0xF6950, 0xF6950, 0xA98A58, 0xF6950, 0xA98A58, 0xF6950, 0x3F2],
        [0x186A0, 0x10F3D8, 0x989680, 0x10EFF0, 0x3E8, 0xA98670, 0x186A0],
        [0xA7DCA8, 0xA7DCA8, 0x2710, 0x186A0, 0xF4240, 0x98C178, 0x98C178],
        [0x10C8E0, 0x98BD90, 0x989680, 0x10F3D8, 0x98BD90, 0x98BD90, 0x10C8E0],
        [0x2710, 0x186A0, 0xF4240, 0x0, 0x0, 0x0, 0x0],
        [0x2710, 0x186A0, 0xF4240, 0xF4240, 0xF4240, 0x186A0, 0x2710],
        [0xF4240, 0x186A0, 0x2710, 0x2710, 0x2710, 0x186A0, 0xF4240],
        [0x0, 0x9A2108, 0x10EFF0, 0x186A0, 0x10EFF0, 0x9A2108, 0x0],
        [0x0, 0x186A0, 0x186A0, 0xA98A58, 0x186A0, 0x186A0, 0x0],
        [0x0, 0x0, 0x0, 0x10C8E0, 0x10C8E0, 0x186A0, 0xF4240],
        [0x0, 0x0, 0x0, 0xA98A58, 0x0, 0x0, 0x0],
        [0x0, 0x0, 0x0, 0x0, 0x0, 0x10C8E0, 0x10C8E0],
        [0x2710, 0x2710, 0x186A0, 0x186A0, 0x186A0, 0xF4240, 0xF4240],
        [0x10EFF0, 0x989A68, 0xA7DCA8, 0x9A2108, 0x98C178, 0x989A68, 0x10EFF0],
        [0x186A0, 0x10C8E0, 0x186A0, 0x186A0, 0x186A0, 0x186A0, 0x10EFF0],
        [0x10EFF0, 0x989A68, 0x3E8, 0x2710, 0x186A0, 0xF4240, 0xA98A58],
        [0xA98A58, 0x3E8, 0x2710, 0x1ADB0, 0x3E8, 0x989A68, 0x10EFF0],
        [0x2710, 0x1ADB0, 0xF6950, 0x98BD90, 0xA98A58, 0x2710, 0x2710],
        [0xA98A58, 0x989680, 0xA98670, 0x3E8, 0x3E8, 0x989A68, 0x10EFF0],
        [0x1ADB0, 0xF4240, 0x989680, 0xA98670, 0x989A68, 0x989A68, 0x10EFF0],
        [0xA98A58, 0x3E8, 0x2710, 0x186A0, 0x186A0, 0x186A0, 0x186A0],
        [0x10EFF0, 0x989A68, 0x989A68, 0x10EFF0, 0x989A68, 0x989A68, 0x10EFF0],
        [0x10EFF0, 0x989A68, 0x989A68, 0x10F3D8, 0x3E8, 0x2710, 0x10C8E0],
        [0x0, 0x10C8E0, 0x10C8E0, 0x0, 0x10C8E0, 0x10C8E0, 0x0],
        [0x10C8E0, 0x10C8E0, 0x0, 0x10C8E0, 0x10C8E0, 0x186A0, 0xF4240],
        [0x2710, 0x186A0, 0xF4240, 0x989680, 0xF4240, 0x186A0, 0x2710],
        [0x0, 0x0, 0xA98A58, 0x0, 0xA98A58, 0x0, 0x0],
        [0x989680, 0xF4240, 0x186A0, 0x2710, 0x186A0, 0xF4240, 0x989680],
        [0x10EFF0, 0x989A68, 0x3E8, 0x2710, 0x186A0, 0x0, 0x186A0],
        [0x10EFF0, 0x989A68, 0x9A2108, 0xA803B8, 0x9A4430, 0x989680, 0x10EFF0],
        [0x186A0, 0xF6950, 0x989A68, 0x989A68, 0xA98A58, 0x989A68, 0x989A68],
        [0xA98670, 0x989A68, 0x989A68, 0xA98670, 0x989A68, 0x989A68, 0xA98670],
        [0x10EFF0, 0x989A68, 0x989680, 0x989680, 0x989680, 0x989A68, 0x10EFF0],
        [0xA95F60, 0x98BD90, 0x989A68, 0x989A68, 0x989A68, 0x98BD90, 0xA95F60],
        [0xA98A58, 0x989680, 0x989680, 0xA98670, 0x989680, 0x989680, 0xA98A58],
        [0xA98A58, 0x989680, 0x989680, 0xA98670, 0x989680, 0x989680, 0x989680],
        [0x10EFF0, 0x989A68, 0x989680, 0x9A4818, 0x989A68, 0x989A68, 0x10F3D8],
        [0x989A68, 0x989A68, 0x989A68, 0xA98A58, 0x989A68, 0x989A68, 0x989A68],
        [0x10EFF0, 0x186A0, 0x186A0, 0x186A0, 0x186A0, 0x186A0, 0x10EFF0],
        [0x3E8, 0x3E8, 0x3E8, 0x3E8, 0x2AF8, 0x989A68, 0x10EFF0],
        [0x989A68, 0x98BD90, 0x9A1D20, 0xA7D8C0, 0x9A1D20, 0x98BD90, 0x989A68],
        [0x989680, 0x989680, 0x989680, 0x989680, 0x989680, 0x989680, 0xA98A58],
        [0x989A68, 0xA803B8, 0x9A2108, 0x9A2108, 0x989A68, 0x989A68, 0x989A68],
        [0x989A68, 0x989A68, 0xA7DCA8, 0x9A2108, 0x98C178, 0x989A68, 0x989A68],
        [0x10EFF0, 0x989A68, 0x989A68, 0x989A68, 0x989A68, 0x989A68, 0x10EFF0],
        [0xA98670, 0x989A68, 0x989A68, 0x989A68, 0xA98670, 0x989680, 0x989680],
        [0x10EFF0, 0x989A68, 0x989A68, 0x989A68, 0x9A2108, 0x98C178, 0x10F3D8],
        [0xA98670, 0x989A68, 0x989A68, 0xA98670, 0x9A1D20, 0x98BD90, 0x989A68],
        [0x10EFF0, 0x989A68, 0x989680, 0x10EFF0, 0x3E8, 0x989A68, 0x10EFF0],
        [0xA98A58, 0x186A0, 0x186A0, 0x186A0, 0x186A0, 0x186A0, 0x186A0],
        [0x989A68, 0x989A68, 0x989A68, 0x989A68, 0x989A68, 0x989A68, 0x10EFF0],
        [0x989A68, 0x989A68, 0x989A68, 0x989A68, 0x989A68, 0xF6950, 0x186A0],
        [0x989A68, 0x989A68, 0x989A68, 0x9A2108, 0x9A2108, 0x9A2108, 0xF6950],
        [0x989A68, 0x989A68, 0xF6950, 0x186A0, 0xF6950, 0x989A68, 0x989A68],
        [0x989A68, 0x989A68, 0x989A68, 0xF6950, 0x186A0, 0x186A0, 0x186A0],
        [0xA98A58, 0x3E8, 0x2710, 0x186A0, 0xF4240, 0x989680, 0xA98A58],
        [0x10EFF0, 0xF4240, 0xF4240, 0xF4240, 0xF4240, 0xF4240, 0x10EFF0],
        [0xF4240, 0xF4240, 0x186A0, 0x186A0, 0x186A0, 0x2710, 0x2710],
        [0x10EFF0, 0x2710, 0x2710, 0x2710, 0x2710, 0x2710, 0x10EFF0],
        [0x186A0, 0xF6950, 0x989A68, 0x0, 0x0, 0x0, 0x0],
        [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xA98A58],
        [0xF4240, 0x186A0, 0x2710, 0x0, 0x0, 0x0, 0x0],
        [0x0, 0x0, 0x10EFF0, 0x989A68, 0x989A68, 0x98C178, 0x10CCC8],
        [0x989680, 0x989680, 0x9A4430, 0xA7DCA8, 0x989A68, 0x989A68, 0xA98670],
        [0x0, 0x0, 0x10EFF0, 0x989A68, 0x989680, 0x989680, 0x10EFF0],
        [0x3E8, 0x3E8, 0x10CCC8, 0x98C178, 0x989A68, 0x989A68, 0x10F3D8],
        [0x0, 0x0, 0x10EFF0, 0x989A68, 0xA98A58, 0x989680, 0x10EFF0],
        [0x1ADB0, 0xF4240, 0xA95F60, 0xF4240, 0xF4240, 0xF4240, 0xF4240],
        [0x10F3D8, 0x989A68, 0x989A68, 0x98C178, 0x10CCC8, 0x3E8, 0x10EFF0],
        [0x989680, 0x989680, 0x9A4430, 0xA7DCA8, 0x989A68, 0x989A68, 0x989A68],
        [0x186A0, 0x0, 0x10C8E0, 0x186A0, 0x186A0, 0x186A0, 0x10EFF0],
        [0x2710, 0x0, 0x1ADB0, 0x2710, 0x2710, 0x2710, 0x10C8E0],
        [0x989680, 0x989680, 0x989A68, 0x98BD90, 0x9A1D20, 0xA7FFD0, 0x989A68],
        [0xF4240, 0xF4240, 0xF4240, 0xF4240, 0xF4240, 0xF4240, 0x186A0],
        [0x0, 0x0, 0xA7FFD0, 0x9A2108, 0x9A2108, 0x9A2108, 0x9A2108],
        [0x0, 0x0, 0x9A4430, 0xA7DCA8, 0x989A68, 0x989A68, 0x989A68],
        [0x0, 0x0, 0x10EFF0, 0x989A68, 0x989A68, 0x989A68, 0x10EFF0],
        [0xA98670, 0x989A68, 0x989A68, 0xA7DCA8, 0x9A4430, 0x989680, 0x989680],
        [0x10F3D8, 0x989A68, 0x989A68, 0x98C178, 0x10CCC8, 0x3E8, 0x3E8],
        [0x0, 0x0, 0x9A1D20, 0xA7FFD0, 0x989680, 0x989680, 0x989680],
        [0x0, 0x0, 0x10EFF0, 0x989680, 0x10EFF0, 0x3E8, 0xA98670],
        [0xF4240, 0xF4240, 0xA98670, 0xF4240, 0xF4240, 0xF4240, 0x1ADB0],
        [0x0, 0x0, 0x989A68, 0x989A68, 0x989A68, 0x98C178, 0x10CCC8],
        [0x0, 0x0, 0x989A68, 0x989A68, 0x989A68, 0xF6950, 0x186A0],
        [0x0, 0x0, 0x9A2108, 0x9A2108, 0x9A2108, 0x9A2108, 0xF6950],
        [0x0, 0x0, 0x989A68, 0xF6950, 0x186A0, 0xF6950, 0x989A68],
        [0x989A68, 0x989A68, 0x989A68, 0x98C178, 0x10CCC8, 0x3E8, 0x10EFF0],
        [0x0, 0x0, 0xA98A58, 0x2710, 0x186A0, 0xF4240, 0xA98A58],
        [0x2710, 0x186A0, 0x186A0, 0xF4240, 0x186A0, 0x186A0, 0x2710],
        [0x186A0, 0x186A0, 0x186A0, 0x0, 0x186A0, 0x186A0, 0x186A0],
        [0xF4240, 0x186A0, 0x186A0, 0x2710, 0x186A0, 0x186A0, 0xF4240],
        [0x0, 0x0, 0xF4628, 0x9A4430, 0x0, 0x0, 0x0],
        [0x10EFF0, 0xF6950, 0xF6950, 0xF6950, 0xF6950, 0xF6950, 0x10EFF0],
    ]
)
gc.collect()


class GRB_Pixel:
    def __init__(
        self, green: uctypes.UINT8 = 0, red: uctypes.UINT8 = 0, blue: uctypes.UINT8 = 0
    ):
        self.green = green
        self.red = red
        self.blue = blue

    def __iter__(self):
        return iter((self.green, self.red, self.blue))

    def __repr__(self):
        return "G: {}, R: {}, B: {}".format(self.green, self.red, self.blue)

    def __bool__(self) -> bool:
        return not not self.green

def char_to_matrix(char: chr) -> numpy.ndarray:
    """all of this because binary_repr is not in ulab numpy!"""
    rows = FONT_MAP[ord(char) - 32]
    rows_padded = ["{0:08}".format(int(row)) for row in rows]  # ensure zero padding.
    rows_as_one_zero_str = [
        list(x) for x in rows_padded
    ]  # increases dimensionality to 2
    # I know this is bad, but before I tie myself in a loop with double comprehension, use a for loop
    rows_as_arrays_of_ints = []
    for row in rows_as_one_zero_str:
        rows_as_arrays_of_ints.append(
            numpy.array([int(x) for x in row], dtype=numpy.uint8)
        )

    char_as_ndarray = numpy.array(rows_as_arrays_of_ints, dtype=numpy.uint8)
    gc.collect()
    return char_as_ndarray


def string_to_matrix(input_: str) -> numpy.array:
    gc.collect()
    characters = tuple([char_to_matrix(x) for x in input_])  # now it's an ndarray
    char_buffer = numpy.concatenate(characters, axis=1)
    return char_buffer


# BUG: Writes the whole matrix upside down...
def matrix_rewrite_serpentine(input_matrix: numpy.ndarray) -> numpy.ndarray:
    #there is a bug in ulab numpy: https://github.com/v923z/micropython-ulab/issues/515
    #input_matrix[:, 1::2] = numpy.flip(input_matrix[:, 1::2], axis=0)
    out = numpy.zeros(input_matrix.T.shape, dtype=input_matrix.dtype)
    # need to iterate over both arrays. Index 0 of Tuple is # of (pre-transpose) columns
    for i in range(input_matrix.T.shape[0]):
        if not i % 2:
            out[i] = input_matrix.T[i]
        out[i] = input_matrix.T[i][::-1]
    return out.T


def matrix_to_pixel_list(
    matrix: numpy.ndarray,
    foreground: GRB_Pixel = GRB_Pixel(255, 0, 0),
    background: GRB_Pixel = GRB_Pixel(0, 0, 0),
    serpentine: bool = True,
    pad_rows: bool = False,  # no, I totally want to do this - but row_stack isn't implemented - will need hand-rolling with some slice-age
) -> list[GRB_Pixel]:

    new_matrix = None
    if pad_rows:
        zero_rows = numpy.zeros((pad_rows, matrix.shape[1]), dtype=numpy.uint8)
        new_matrix = numpy.row_stack((matrix, zero_rows))

    else:
        new_matrix = matrix

    if serpentine:
        new_matrix = matrix_rewrite_serpentine(new_matrix)
    ravelled = new_matrix.flatten(order="F")
    as_list = ravelled.tolist()
    as_pixels = [(background, foreground)[x] for x in as_list]
    return as_pixels


def scroll_text(
    message: str,
    serpentine: bool = True,
    foreground: GRB_Pixel = GRB_Pixel(128, 0, 0),
    background: GRB_Pixel = GRB_Pixel(0, 0, 0),
    framerate: int = 40,
):
    message_matrix: numpy.array = string_to_matrix(message)
    pixels: neopixel.NeoPixel = neopixel.NeoPixel(Pin(LED_PIN, Pin.OUT), LED_FIELD)

    left_pad, right_pad = 2 * (
        numpy.zeros((LED_HEIGHT - 1, LED_WIDTH), dtype=numpy.uint8),
    )

    padded_matrix = numpy.concatenate((left_pad, message_matrix, right_pad), axis=1)
    # Reverse the boundaries if scrolling right
    boundaries = (0, padded_matrix.shape[1])[::SCROLL_DIRECTION]
    boundaries = (0, message_matrix.shape[1])[::SCROLL_DIRECTION]
    scroll_start, scroll_end = boundaries

    # Scroll through the text
    for i in range(scroll_start, scroll_end, SCROLL_DIRECTION):
        a_bound = i
        b_bound = i + (SCROLL_DIRECTION * LED_WIDTH)
        left_bound = min(a_bound, b_bound)
        right_bound = max(a_bound, b_bound)
        # display = padded_matrix[:, left_bound:right_bound]
        display = message_matrix[:, left_bound:right_bound]
        display_pixels = matrix_to_pixel_list(
            display, foreground=foreground, background=background, serpentine=True
        )
        # looks like uPy NeoPixel doesn't support slices...
        # pixels[0 : len(display_pixels) - 1] = display_pixels
        for i in range(len(display_pixels)):
            g, r, b = display_pixels[i]
            pixels[i] = (g, r, b)
        pixels.write()
        gc.collect()
        # add some framerate control that accounts for computation time...


def wifi_connect() -> None:
    status_led = Pin(LED_INTERNAL_PIN, Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    print("setting wifi active")
    wlan.active(True)
    status_led.on()
    print("attempting wifi connect")
    wlan.connect(WIFI_ESSID, WIFI_KEY)
    while not wlan.isconnected():
        status_led.off()
        time.sleep_ms(500)
        status_led.on()
        print("wifi still not connected... sleeping")

    print("wifi connected!")
    for _ in range(5):
        status_led.off()
        time.sleep_ms(100)
        status_led.on()


def fetch_message() -> str:
    # FIXME implement appropriate HTTP GET logic
    return f" {ENDPOINT_URI} Hello, World!"


def run():
    #wifi_connect()
    gc.collect()
    if message := fetch_message():
        print(f"printing {message}")
        scroll_text(message)
        print("Finished printing - going to sleep")


def emulate(pixel_list: listi, emulate_serpentine: bool = False):
    field = numpy.zeros((LED_HEIGHT, LED_WIDTH), dtype=numpy.uint8)
    row, col = 0, 0
    for i in range(LED_FIELD - 1):
        if row == (LED_HEIGHT - 1):
            # End of row
            col += 1
            row = 0
        elif col >= (LED_WIDTH - 1):
            # Skip pixels out of field
            continue
        if emulate_serpentine and (col % 2):
            print("flip this column")
            field[(LED_HEIGHT-row) - 1][col] = (0,1)[not not pixel_list[i]]
        else:
            print("no flip")
            field[row][col] = (0,1)[not not pixel_list[i]]
        row += 1
    for row in field:
        rowlst = row.tolist()
        printable = [(" ","*")[not not x] for x in rowlst]
        print("".join(printable))


if __name__ == "__main__":
    #while True:
    #    run()
    #    time.sleep(5)
    mat = string_to_matrix("Hello friends")
    test_list = matrix_to_pixel_list(mat, serpentine=False)
    emulate(test_list, emulate_serpentine=False)
