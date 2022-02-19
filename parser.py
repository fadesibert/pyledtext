import numpy

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

if __name__ == "__main__":
    font_map = translate_header_file()
    print("font_map = [")
    for char_ in font_map:
        contents = ", ".join([hex(int(row)) for row in char_])
        print(f"[{contents}], ")
    print("]")
