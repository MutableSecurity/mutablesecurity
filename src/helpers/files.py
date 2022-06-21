"""Module containing files processing functionality."""

import pathlib
import typing


def read_file_lines(
    path: pathlib.Path,
) -> typing.Generator[str, None, None]:
    """Parse a file containing connection strings.

    See the function parse_connection_string for format information.

    Args:
        path (pathlib.Path): File with connection string

    Yields:
        str: Line in the file
    """
    with open(path, "r", encoding="utf-8") as remote_hosts:
        for line in remote_hosts.readlines():
            line = line.strip()
            if not line:
                continue

            yield line
