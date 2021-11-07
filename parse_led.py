import time
from dataclasses import dataclass, fields
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


def row_to_binary_str(row: str) -> str:
    if row.strip()[0:2:1] == "0x":
        line = eval(row.strip()[0:42])
        binary = [f"{x:08b}" for x in line]
        return binary
    else:
        return None


def led_test_render(character) -> str:
    char_led = []
    for line in character:
        char_led.append("".join([(" ", "*")[int(x)] for x in line]))
    return "\n".join(char_led)


def translate_header_file(filename: str) -> list[list[int]]:
    ascii_char_map = []

    with open("FontMatrise.h") as fh:
        x = [row_to_binary_str(row) for row in fh.readlines()]
        [ascii_char_map.append(y) for y in x if y]

    return ascii_char_map


def char_to_led_test(char: chr) -> str:
    return led_test_render(char_to_matrix(char))


def char_to_matrix(char: chr) -> numpy.matrix:
    rows = CHAR_MAP[ord(char) - 32]
    rows_n = []
    for row in rows:
        rows_n.append([int(x) for x in row])

    return numpy.asmatrix(rows_n, dtype="i8")


def string_to_matrix(input: str):
    characters = [char_to_matrix(x) for x in input]
    char_buffer = numpy.concatenate(characters, 1)
    return char_buffer


def matrix_to_pixels(
    matrix: numpy.matrix,
    foreground: GRB_Pixel = GRB_Pixel(255, 0, 0),
):
    transformed_type = matrix.astype("i8,i8,i8")
    ravelled = transformed_type.ravel()
    with numpy.nditer(ravelled, op_flags=["readwrite"]) as nd:
        for x in nd:
            if (x.item()) == (1, 1, 1):
                x[...] = tuple(foreground.__list__())

    return ravelled.reshape(transformed_type.shape)


def matrix_rewrite_serpentine(input: numpy.matrix) -> numpy.matrix:
    input[1::2, :] = input[1::2, ::-1]
    return input


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
    if not emulate:
        pixels = neopixel.NeoPixel(board.D21, num_pixels, brightness=brightness)
    # Scrolling
    for i in range(-message_width, message_width):
        display = numpy.roll(filled_matrix, i)[:, 0:LED_WIDTH]
        # replace this with a neopixel call - or buffer this since we have the memory on a pi?
        if emulate:
            print(display)
        else:
            pixels[0:LED_WIDTH] = filled_matrix.ravel().tolist()[0]
        time.sleep(1 / scroll_speed)


if __name__ == "__main__":
    fn = "FontMatrise.h"
    CHAR_MAP = translate_header_file(fn)
    hw = "Hello, World"
    scroll_text(hw, 32, 8, ScrollDirection.LEFT, 20, False)
