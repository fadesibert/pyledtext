import numpy
import neopixel
from machine import const, Pin
import uctypes

LEFT  = const(1)
RIGHT = const(-1)
LED_PIN = const(21)  # Modify this value to change LED Pin. Refer to Pinout Diagram
LED_BRIGHTNESS = const(50) # value out 100
LED_BRIGHT_MULT = const(int(LED_BRIGHTNESS / 255))

LED_WIDTH = const(96)
LED_HEIGHT = const(8)
LED_FIELD = const(LED_WIDTH * LED_HEIGHT)

SCROLL_DIRECTION_LEFT = const(1)
SCROLL_DIRECTION_RIGHT = const(-1)

# Using Consts as Enum not supported in MicroPython
SCROLL_DIRECTION = SCROLL_DIRECTION_LEFT # change this using another const

class GRB_Pixel:
    def __init__(self, green: uctypes.UINT8 = 0, red: uctypes.UINT8 = 0, blue: uctypes.UINT8 = 0):
        self.green = green
        self.red  = red
        self.blue = blue

    def __iter__(self):
        return iter((self.green, self.red, self.blue))

def char_to_matrix(char: chr) -> numpy.matrix:
    rows = CHAR_MAP[ord(char) - 32]
    rows_n = []
    for row in rows:
        rows_n.append([int(x) for x in row])
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

    ravelled = new_matrix.ravel('F')
    as_list = ravelled.tolist()[0]

    as_pixels = [(background, foreground)[x] for x in as_list]

    return as_pixels


def scroll_text(
    message: str,
    scroll_direction: ScrollDirection,
    serpentine: bool = True,
    pixels_per_char: int = 8,
    foreground: GRB_Pixel = GRB_Pixel(255, 0, 0),
    background: GRB_Pixel = GRB_Pixel(0, 0, 0),
    framerate: int = 40
):
    num_pixels = LED_WIDTH * LED_HEIGHT
    message_matrix = string_to_matrix(message)
    pixels = neopixel.NeoPixel(Pin(D21, Pin.OUT), num_pixels)

    left_pad, right_pad = 2 * (numpy.matrix(numpy.zeros((LED_HEIGHT-1, LED_WIDTH), dtype=int)),)
    padded_matrix = numpy.concatenate((left_pad, message_matrix, right_pad),1)
    # Reverse the boundaries if scrolling right
    boundaries = (0, padded_matrix.shape[1])[::SCROLL_DIRECTION]
    scroll_start, scroll_end = boundaries

    # Scroll through the text
    for i in range(scroll_start, scroll_end, scroll_direction.value):
        a_bound = i
        b_bound = i + (scroll_direction.value * LED_WIDTH)
        left_bound = min(a_bound, b_bound)
        right_bound = max(a_bound, b_bound)
        display = padded_matrix[:, left_bound:right_bound]
        display_pixels = matrix_to_pixel_list(display, foreground=foreground, background=background, serpentine=True)
        pixels[0: len(display_pixels) - 1] = display_pixels


def display_text(
    message: str,
    LED_WIDTH: int,
    LED_HEIGHT: int,
    serpentine: bool = True,
    pixels_per_char: int = 8,
):

    message_matrix = string_to_matrix(message)

    message_pixels = matrix_to_pixel_list(message_matrix, background=GRB_Pixel(12, 12, 12))
    pixels = neopixel.NeoPixel(Pin(21, Pin.OUT), LED_FIELD)
    pixels[0:LED_FIELD-1] = message_pixels[0:LED_FIELD]

if __name__ == "__main__":
    # set CPU speed
    # configure wifi
    ASCII_OFFSET=32
    i = ASCII_OFFSET
    for row in translate_header_file():
        # set CPU speed
        # configure wifi
        #print(f'{i=} {chr(i)}\t' + '\t'.join(row).expandtabs(10))
        print('|'.join(row))
        #i += 1
    # sleep
