"""Module with operations for managing crontabs."""
import typing

from pyinfra.api import Host, State, operation

# pylint: disable=unused-argument


@operation
def remove_crontabs(
    unique_identifier: str,
    state: typing.Optional[Host] = None,
    host: typing.Optional[State] = None,
) -> typing.Generator[str, None, None]:
    """Remove crontabs identified by a string.

    Args:
        unique_identifier (str): Removed crontabs identifier
        state (Host, optional): State. Defaults to None.
        host (State, optional): Host. Defaults to None.

    Yields:
        Iterator[typing.Generator[str, None, None]]: Command to execute
    """
    yield f"crontab -l | grep -v '{unique_identifier}' | sudo crontab -"
