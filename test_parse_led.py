import numpy
import pytest
from pyledtext import parse_led

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
