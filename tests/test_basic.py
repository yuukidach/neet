import pytest

from neet.trace import Value, make_traceable


@make_traceable
def add(a, b):
    return a + b


@make_traceable
def mul(a, b):
    return a * b


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 9),
        (2, 3, 50),
    ],
)
def test_single_path(a, b, expected):
    a = Value(a)
    b = Value(b)
    c = add(a, b)
    d = mul(c, c)
    e = mul(d, a)

    assert e.data == expected


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
