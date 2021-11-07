import time
from dataclasses import astuple, dataclass, fields
from enum import Enum

import board
import neopixel
import numpy

CHAR_MAP = []


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
        return iter(astuple(self))

def row_to_binary_str(row: str) -> str:
    if row.strip()[0:2:1] == "0x":
        line = eval(row.strip()[0:42])
        binary = [f"{x:08b}" for x in line]
        return binary
    else:
        return None


def translate_header_file(filename: str) -> list[list[int]]:
    ascii_char_map = []

    with open("FontMatrise.h") as fh:
        x = [row_to_binary_str(row) for row in fh.readlines()]
        [ascii_char_map.append(y) for y in x if y]

    return ascii_char_map

def _handle_row(row: list[str]) -> str:
    new_row = [(" ", "*")[cell] for cell in row]
    return "".join(new_row)

def render_matrix_ascii(matrix: numpy.matrix) -> list[str]:
    display = [_handle_row(row) for row in matrix.tolist()]
    return display

def char_to_matrix(char: chr) -> numpy.matrix:
    rows = CHAR_MAP[ord(char) - 32]
    rows_n = []
    for row in rows:
        rows_n.append([int(x) for x in row])
    return numpy.asmatrix(rows_n, dtype="i8")


def string_to_matrix(input: str):
    characters = [char_to_matrix(x) for x in input]
    char_buffer = numpy.concatenate(characters, 1)
    zero_row = numpy.zeros(char_buffer.shape[1], dtype=int)
    with_bottom_row = numpy.row_stack((char_buffer, zero_row))
    return with_bottom_row


def matrix_rewrite_serpentine(input: numpy.matrix) -> numpy.matrix:
    input[1::2, :] = input[1::2, ::-1]
    return input


def matrix_to_pixel_list(
    matrix: numpy.matrix,
    foreground: GRB_Pixel = GRB_Pixel(255, 0, 0),
    background: GRB_Pixel = GRB_Pixel(0, 0, 0),
    serpentine: bool = True,
) -> list[GRB_Pixel]:
    # need to trim to correct buffer size before altering shape
    if serpentine:
        matrix = matrix_rewrite_serpentine(matrix)
        [print(row) for row in render_matrix_ascii(matrix)]
    print(f'RxC: {matrix.shape}')
    ravelled = matrix.ravel('F')
    as_list = ravelled.tolist()[0]
    as_pixels = [(background, foreground)[x] for x in as_list]
    
    return as_pixels


def scroll_text(
    message: str,
    LED_WIDTH: int,
    LED_HEIGHT: int,
    scroll_direction: ScrollDirection,
    scroll_speed: int = 20,
    serpentine: bool = True,
    pixels_per_char: int = 8,
    emulate: bool = False,
    brightness: float = 0.01,
):
    num_pixels = LED_WIDTH * LED_HEIGHT
    matrix = matrix_to_pixels(string_to_matrix(message))
    message_height, message_width = matrix.shape
    buffer_width = LED_WIDTH * pixels_per_char * 2
    filler_width = buffer_width - message_width
    zeroes = numpy.asmatrix(numpy.full((message_height, filler_width), 0, dtype="i8,i8,i8"))
    filled_matrix = numpy.concatenate((matrix.T, zeroes.T)).T


def display_text(
    message: str,
    LED_WIDTH: int,
    LED_HEIGHT: int,
    serpentine: bool = True,
    pixels_per_char: int = 8,
    brightness: float = 0.01,
):
    num_pixels = LED_WIDTH * LED_HEIGHT
    message_matrix = string_to_matrix(message)
    txt = render_matrix_ascii(message_matrix)
    [print(x) for x in txt]
    
    message_pixels = matrix_to_pixel_list(message_matrix, background=GRB_Pixel(12, 12, 12))
    pixels = neopixel.NeoPixel(board.D21, num_pixels, brightness=brightness)
    pixels[0:num_pixels] = message_pixels

if __name__ == "__main__":
    fn = "FontMatrise.h"
    CHAR_MAP = translate_header_file(fn)
    hw = "a    "
    display_text(hw, 32, 8, serpentine=True, brightness=0.1)
