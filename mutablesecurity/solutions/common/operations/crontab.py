"""Module with operations for managing crontabs."""
import typing

from pyinfra.api import operation


@operation
def remove_crontabs_by_part(
    unique_part: str,
) -> typing.Generator[str, None, None]:
    """Remove a crontab by a unique identifier.

    Args:
        unique_part (str): Unique identifier

    Yields:
        Iterator[typing.Generator[str, None, None]]: Command to execute
    """
    yield f"crontab -l | grep -v '{unique_part}' | sudo crontab -"
