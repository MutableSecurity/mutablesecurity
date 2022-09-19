"""Module with apt operations."""
import typing

from pyinfra.api import operation


@operation
def autoremove() -> typing.Generator[str, None, None]:
    """Removes residual data automatically.

    Args:
        no args

    Yields:
        Iterator[typing.Generator[str, None, None]]: Command to execute
    """
    yield "apt -y autoremove"
