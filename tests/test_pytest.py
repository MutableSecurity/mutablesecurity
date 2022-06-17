"""Module for testing if pytest is working."""


def inc(number: int) -> int:
    """Increments a number.

    Args:
        number (int): Number to increment

    Returns:
        int: Incremented number
    """
    return number + 1


def test_answer() -> None:
    """Tests a simple assertion."""
    assert inc(3) == 4
