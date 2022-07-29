"""Module containing files processing functionality."""

import pathlib
import typing

from mutablesecurity.helpers.exceptions import (
    FileNotExistsException,
    ImproperPermissionsException,
)


def read_file_lines(
    path: pathlib.Path,
) -> typing.List[str]:
    """Parse and strip a file containing text lines.

    To be used only with reasonable files. An implementation using yield is
    better for larger files.

    Args:
        path (pathlib.Path): Path to existent file

    Raises:
        FileNotExistsException: File does not exists.
        ImproperPermissionsException: Improper permissions

    Returns:
        str: List of lines in files
    """
    try:
        if not path.exists():
            raise FileNotExistsException()
    except PermissionError as exception:
        raise ImproperPermissionsException() from exception

    with open(path, "r", encoding="utf-8") as opened_file:
        lines = []
        for line in opened_file.readlines():
            line = line.strip()
            if not line:
                continue

            lines.append(line)

        return lines
