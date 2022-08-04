"""Module with operations for managing files."""
import typing

from pyinfra.api import operation


@operation
def append_line_to_file(
    path: str,
    line: str,
) -> typing.Generator[str, None, None]:
    """Append a line into a file.

    Args:
        path (str): File path
        line (str): Line to be added

    Yields:
        Iterator[typing.Generator[str, None, None]]: Command to execute
    """
    yield f"echo '{line}' | tee --append {path}"
