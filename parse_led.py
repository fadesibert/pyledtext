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
        #time.sleep(0.65 / framerate) # compensate for compute time

def blink_cursor(
    scroll_direction: ScrollDirection,
    num_blinks: int = 10,
    box_width: int = 6,
    duty_cycle: float = 0.8,
    LED_WIDTH: int = 96,
    LED_HEIGHT: int = 8,
    serpentine: bool = True,
    foreground: GRB_Pixel = GRB_Pixel(255, 0, 0),
    background: GRB_Pixel = GRB_Pixel(0, 0, 0),
    brightness: float = 0.1
):
    import board
    import neopixel

    num_pixels = LED_WIDTH * LED_HEIGHT
    box = numpy.matrix(numpy.ones((LED_HEIGHT, box_width), dtype=int))
    line_blank = numpy.zeros((LED_HEIGHT - 1, box_width), dtype=int)
    line = numpy.matrix(numpy.vstack((line_blank, [1] * box_width)))
    box_pixels = matrix_to_pixel_list(box, foreground=foreground, background=background, serpentine=True, pad_rows=0)
    line_pixels = matrix_to_pixel_list(line, foreground=foreground, background=background, serpentine=True, pad_rows=0)
    cursor_boundary = len(box_pixels)

    with neopixel.NeoPixel(board.D21, num_pixels, brightness=brightness) as pixels:
        for _ in range(num_blinks):
            pixels[0:cursor_boundary] = box_pixels
            time.sleep(duty_cycle)
            pixels[0:cursor_boundary] = line_pixels
            time.sleep(1.0 - duty_cycle)


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
    hw = "Penny is the best girlfriend of all time!"
    #cProfile.run(
    #    'scroll_text(hw, 96, 8, serpentine=True, brightness=0.1, scroll_direction=ScrollDirection.LEFT)'
    #)
    scroll_text(hw, 96, 8, serpentine=True, brightness=0.1, scroll_direction=ScrollDirection.LEFT)
    #blink_cursor(ScrollDirection.LEFT, duty_cycle=0.7, foreground=GRB_Pixel(157, 206, 217))
