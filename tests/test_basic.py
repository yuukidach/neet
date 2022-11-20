import pytest

from neet.trace import Value, make_traceable, Tracer


@make_traceable
def add(a, b):
    """Add two numbers."""
    print(f"Adding {a} and {b}")
    return a + b


@make_traceable
def mul(a, b):
    """Multiply two numbers."""
    print(f"Multiplying {a} and {b}")
    return a * b


class CallableClass:
    def __init__(self) -> None:
        self._value = 0

    def __call__(self, value: int) -> int:
        self._value += value
        return self._value


def test_docstring():
    assert add.__doc__ == "Add two numbers."
    assert mul.__doc__ == "Multiply two numbers."


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 9),
        (2, 3, 50),
    ],
)
def test_with_tracer(a, b, expected):
    with Tracer():
        a = Value(a)
        b = Value(b)
        c = add(a, b)
        print("This is the first print")
        d = mul(c, c)
        e = mul(d, a)

    assert e.data == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 3),
        (2, 3, 5),
    ],
)
def test_without_tracer(a, b, expected):
    assert add(a, b) == expected


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
