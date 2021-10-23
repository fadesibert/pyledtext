CHAR_MAP = []

def row_to_binary(row: str) -> str:
    if row.strip()[0:2:1] == "0x":
        line = eval(row.strip()[0:42])
        binary = [f'{x:08b}' for x in line]
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

    with open('FontMatrise.h') as fh:
        x = [row_to_binary(row) for row in fh.readlines()]
        [ascii_char_map.append(y) for y in x if y]

    return ascii_char_map


def char_to_led_test(char: chr) -> str:
    return led_test_render(char_to_matrix(char))

def char_to_matrix(char: chr) -> list[int]:
    return CHAR_MAP[ord(char) - 32]

if __name__ == "__main__":
    fn = 'FontMatrise.h'
    CHAR_MAP = translate_header_file(fn)
    hw = "Hello, World"
    [print(char_to_led_test(x)) for x in hw]
    [print(char_to_matrix(x)) for x in hw]
