from array import array
from ulab import numpy
import neopixel
from math import floor
from machine import const, Pin
import uctypes

# hack when running *nix micropython port
# const = lambda x: int(x)

LEFT = const(1)
RIGHT = const(-1)
LED_PIN = const(21)  # Modify this value to change LED Pin. Refer to Pinout Diagram
LED_BRIGHTNESS = const(50)  # value out 100
LED_BRIGHT_MULT = int(floor((LED_BRIGHTNESS / 255)))

LED_WIDTH = const(96)
LED_HEIGHT = const(8)
LED_FIELD = const(LED_WIDTH * LED_HEIGHT)

SCROLL_DIRECTION_LEFT = const(1)
SCROLL_DIRECTION_RIGHT = const(-1)

WIFI_ESSID = "AnyNetwork"
WIFI_KEY = "SomeBigHugeSecret"

ENDPOINT_URI = "https://myfancyapi.com/messages/"

# Using Consts as Enum not supported in MicroPython
SCROLL_DIRECTION = SCROLL_DIRECTION_LEFT  # change this using another const

# 2D Arrays not yet supported
# Once basic functionality established, switch to memoryview, array or const
FONT_MAP = [
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


class GRB_Pixel:
    def __init__(self, green: uctypes.UINT8 = 0, red: uctypes.UINT8 = 0, blue: uctypes.UINT8 = 0):
        self.green = green
        self.red = red
        self.blue = blue

    def __iter__(self):
        return iter((self.green, self.red, self.blue))


def char_to_matrix(char: chr) -> numpy.matrix:
    rows = FONT_MAP[ord(char) - 32]
    rows_n = array("i", [int(x) for x in row])
    return numpy.asmatrix(rows_n, dtype="i8")


# Todo make this an array rather than list
def string_to_matrix(input: str):
    characters = [char_to_matrix(x) for x in input]
    char_buffer = numpy.concatenate(characters, 1)
    return char_buffer


def matrix_rewrite_serpentine(input_matrix: numpy.matrix) -> numpy.matrix:
    input_matrix[:, 1::2] = numpy.flipud(input_matrix[:, 1::2])
    return input_matrix


def matrix_to_pixel_list(
    matrix: numpy.matrix,
    foreground: GRB_Pixel = GRB_Pixel(255, 0, 0),
    background: GRB_Pixel = GRB_Pixel(0, 0, 0),
    serpentine: bool = True,
    pad_rows: int = 1,
) -> list[GRB_Pixel]:
    new_matrix = None

    if pad_rows:
        zero_rows = numpy.zeros((pad_rows, matrix.shape[1]), dtype=int)
        new_matrix = numpy.row_stack((matrix, zero_rows))

    else:
        new_matrix = matrix

    if serpentine:
        new_matrix = matrix_rewrite_serpentine(new_matrix)

    ravelled = new_matrix.ravel("F")
    as_list = ravelled.tolist()[0]

    as_pixels = [(background, foreground)[x] for x in as_list]

    return as_pixels


def scroll_text(
    message: str,
    serpentine: bool = True,
    foreground: GRB_Pixel = GRB_Pixel(255, 0, 0),
    background: GRB_Pixel = GRB_Pixel(0, 0, 0),
    framerate: int = 40,
):
    message_matrix = string_to_matrix(message)
    pixels = neopixel.NeoPixel(Pin(LED_PIN, Pin.OUT), LED_FIELD)

    left_pad, right_pad = 2 * (numpy.matrix(numpy.zeros((LED_HEIGHT - 1, LED_WIDTH), dtype=int)),)
    padded_matrix = numpy.concatenate((left_pad, message_matrix, right_pad), 1)
    # Reverse the boundaries if scrolling right
    boundaries = (0, padded_matrix.shape[1])[::SCROLL_DIRECTION]
    scroll_start, scroll_end = boundaries

    # Scroll through the text
    for i in range(scroll_start, scroll_end, SCROLL_DIRECTION):
        a_bound = i
        b_bound = i + (SCROLL_DIRECTION * LED_WIDTH)
        left_bound = min(a_bound, b_bound)
        right_bound = max(a_bound, b_bound)
        display = padded_matrix[:, left_bound:right_bound]
        display_pixels = matrix_to_pixel_list(display, foreground=foreground, background=background, serpentine=True)
        pixels[0 : len(display_pixels) - 1] = display_pixels


def wifi_connect() -> None:
    pass


def fetch_message() -> str:
    # FIXME implement appropriate HTTP GET logic
    return f" {ENDPOINT_URI} Hello, World!"


if __name__ == "__main__":
    # set CPU speed
    # configure wifi
    ASCII_OFFSET = 32
    i = ASCII_OFFSET
    for char_ in FONT_MAP:
        # set CPU speed
        # configure wifi
        # print(f'{i=} {chr(i)}\t' + '\t'.join(row).expandtabs(10))
        print(chr(i))
        for row in char_:
            print(row)

        i += 1
    # sleep
