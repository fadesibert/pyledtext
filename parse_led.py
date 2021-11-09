import time
from dataclasses import astuple, dataclass, fields
from enum import Enum

import board
import neopixel
import numpy
import cProfile

# These are used in setup
def translate_header_file(filename: str = "FontMatrise.h") -> list[list[int]]:
    ascii_char_map = []

    with open(filename) as fh:
        x = [row_to_binary_str(row) for row in fh.readlines()]
        [ascii_char_map.append(y) for y in x if y]

    return ascii_char_map

def row_to_binary_str(row: str) -> list[str]:
    if row.strip()[0:2:1] == "0x":
        line = eval(row.strip()[0:42])
        binary = [f"{x:08b}" for x in line]
        return binary
    else:
        return None


CHAR_MAP = translate_header_file()


class PixelRangeError(Exception):
    def __init__(self, name, value):
        message = f"{name} not between 0 and 255: {value}"
        super().__init__(self, message)


class ScrollDirection(Enum):
    LEFT = 1
    RIGHT = -1

    # Up, Down not supported


@dataclass
class GRB_Pixel:
    green: int = 0
    red: int = 0
    blue: int = 0

    def __post_init__(self):
        for field in fields(self):
            value = self.__getattribute__(field.name)
            if 0 <= value <= 255:
                pass
            else:
                raise PixelRangeError(field.name, value)

    def __list__(self):
        return [self.green, self.red, self.blue]

    def __len__(self):
        return 3

    def __iter__(self):
        return iter((self.green, self.red, self.blue))


def _handle_row(row: list[str]) -> str:
    new_row = [(" ", "*")[cell] for cell in row]
    return "".join(new_row)

def render_matrix_ascii(matrix: numpy.matrix) -> list[str]:
    display = [_handle_row(row) for row in matrix.tolist()]
    return display

def char_to_matrix(char: chr) -> numpy.matrix:
    global CHAR_MAP
    rows = CHAR_MAP[ord(char) - 32]
    rows_n = []
    for row in rows:
        rows_n.append([int(x) for x in row])
    return numpy.asmatrix(rows_n, dtype="i8")


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
) -> list[GRB_Pixel]:
    zero_row = numpy.zeros(matrix.shape[1], dtype=int)
    with_bottom_row = numpy.row_stack((matrix, zero_row))

    if serpentine:
        with_bottom_row = matrix_rewrite_serpentine(with_bottom_row)

    ravelled = with_bottom_row.ravel('F')
    as_list = ravelled.tolist()[0]
    
    as_pixels = [(background, foreground)[x] for x in as_list]

    return as_pixels


def scroll_text(
    message: str,
    LED_WIDTH: int,
    LED_HEIGHT: int,
    scroll_direction: ScrollDirection,
    serpentine: bool = True,
    pixels_per_char: int = 8,
    brightness: float = 0.01,
    foreground: GRB_Pixel = GRB_Pixel(255, 0, 0),
    background: GRB_Pixel = GRB_Pixel(0, 0, 0),
    framerate: int = 40
):
    import board
    import neopixel

    num_pixels = LED_WIDTH * LED_HEIGHT
    message_matrix = string_to_matrix(message)
    pixels = neopixel.NeoPixel(board.D21, num_pixels, brightness=brightness)

    left_pad, right_pad = 2 * (numpy.matrix(numpy.zeros((LED_HEIGHT-1, LED_WIDTH), dtype=int)),)
    padded_matrix = numpy.concatenate((left_pad, message_matrix, right_pad),1)
    # Reverse the boundaries if scrolling right
    boundaries = (0, padded_matrix.shape[1])[::scroll_direction.value]
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
        time.sleep(0.65 / framerate) # compensate for compute time

def display_text(
    message: str,
    LED_WIDTH: int,
    LED_HEIGHT: int,
    serpentine: bool = True,
    pixels_per_char: int = 8,
    brightness: float = 0.01,
):
    import board
    import neopixel
    num_pixels = LED_WIDTH * LED_HEIGHT
    message_matrix = string_to_matrix(message)

    message_pixels = matrix_to_pixel_list(message_matrix, background=GRB_Pixel(12, 12, 12))
    pixels = neopixel.NeoPixel(board.D21, num_pixels, brightness=brightness)
    pixels[0:num_pixels-1] = message_pixels[0:num_pixels]

if __name__ == "__main__":
    hw = "This is a very quick test message"
    #cProfile.run(
    #    'scroll_text(hw, 96, 8, serpentine=True, brightness=0.1, scroll_direction=ScrollDirection.LEFT)'
    #)
    scroll_text(hw, 96, 8, serpentine=True, brightness=0.1, scroll_direction=ScrollDirection.LEFT)
