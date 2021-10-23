from dataclasses import dataclass, fields

import numpy

CHAR_MAP = []


class PixelRangeError(Exception):
    def __init__(self, name, value):
        message = f"{name} not between 0 and 255: {value}"
        super().__init__(self, message)


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


def row_to_binary(row: str) -> str:
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
        x = [row_to_binary(row) for row in fh.readlines()]
        [ascii_char_map.append(y) for y in x if y]

    return ascii_char_map


def char_to_led_test(char: chr) -> str:
    return led_test_render(char_to_matrix(char))


def char_to_matrix(char: chr) -> list[int]:
    return CHAR_MAP[ord(char) - 32]


def string_to_matrix(input: str):
    characters = [char_to_matrix(x) for x in input]
    rowlist = numpy.concatenate(characters)
    char_buffer = rowlist.reshape(7, len(str))
    return char_buffer


def matrix_to_pixels(matrix: numpy.matrix, default_color=(255, 0, 0)):
    pass


if __name__ == "__main__":
    fn = "FontMatrise.h"
    CHAR_MAP = translate_header_file(fn)
    hw = "Hello, World"
    print(string_to_matrix(hw))
