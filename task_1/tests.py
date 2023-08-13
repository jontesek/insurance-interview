import pytest

from .main import find_max_sum, find_max_sum_rec


TEST_DATA = [
    ([155, 55, 2, 96, 67, 203, 3], 454),
    ([155, 54, 3, 10], 165),
    ([12, 43, 10, 8, 90, 123, 5, 3, 56], 230),
    ([1, 10, 200, 154, 160, 289, 454, 5, 10, 34], 849),
    ([347, 440, 342, 297, 104, 118, 119, 268, 218], 1130),
    ([463, 73, 282, 422, 271, 118, 112], 1128),
]


@pytest.mark.parametrize("test_input,expected", TEST_DATA)
def test_main(test_input, expected):
    assert find_max_sum(test_input) == expected


@pytest.mark.parametrize("test_input,expected", TEST_DATA)
def test_main_recursive(test_input, expected):
    assert find_max_sum_rec(test_input) == expected
