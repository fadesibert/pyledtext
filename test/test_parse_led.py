import numpy
import pytest
from pyledtext import parse_led

@pytest.mark.filterwarnings("ignore:.*:PendingDeprecationWarning")
class TestPyLedTest:

    def test_row_to_binary(self):
        test_row = '         0x00, 0x00, 0x00, 0x60, 0x60, 0x20, 0x40,  // Code for char ,'
        expected_result = ['00000000', '00000000', '00000000', '01100000', '01100000', '00100000', '01000000']

        test_output = parse_led.row_to_binary_str(test_row)

        assert expected_result == test_output

    def test_render_matrix_ascii(self):
        test_matrix_square = numpy.matrix([
            [1, 0, 1],
            [1, 1, 0],
            [0, 1, 0]
        ])

        expected_output_square = ["* *", "** ", " * "]
        assert expected_output_square == parse_led.render_matrix_ascii(test_matrix_square)

        test_matrix_long = numpy.matrix([
            [1, 0, 0, 0, 0, 1],
            [0, 0, 1, 1, 0, 1]
        ])

        expected_output_long = ["*    *", "  ** *"]
        assert expected_output_long == parse_led.render_matrix_ascii(test_matrix_long)

    def test_char_to_matrix(self):
        expected_output_a = numpy.matrix([
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 0, 0],
            [1, 0, 0, 1, 1, 0, 0, 0],
            [0, 1, 1, 0, 1, 0, 0, 0]
        ])
        test_output_a = parse_led.char_to_matrix("a")
        assert (expected_output_a == test_output_a).all()

    def test_string_to_matrix(self):
        pass

    def test_matrix_rewrite_serpentine(self):
        test_matrix = numpy.matrix([
            [0, 1, 1, 1],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
            [1, 1, 1, 0]
        ])
        expected_output = numpy.matrix([
            [0, 1, 1, 0],
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 1]
        ])

        test_output = parse_led.matrix_rewrite_serpentine(test_matrix)

        assert (expected_output == test_output).all()

    def test_matrix_to_pixel_list(self):
        fg = parse_led.GRB_Pixel(255, 0, 0)
        bg = parse_led.GRB_Pixel(0, 0, 128)

        test_matrix_small = numpy.matrix([
            [1, 0, 1],
            [1, 0, 0],
            [0, 1, 1],
        ])

        expected_output_small = [
            fg, fg, bg, bg,
            bg, fg, bg, bg,
            fg, bg, fg, bg,
        ]

        test_output_small = parse_led.matrix_to_pixel_list(test_matrix_small, foreground=fg, background=bg, serpentine=True)
        assert expected_output_small == test_output_small
