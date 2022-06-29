"""Module for testing helper file operations."""

import tempfile
from pathlib import Path

import pytest

from src.helpers.exceptions import FileNotExists, ImproperPermissionsException
from src.helpers.files import read_file_lines


def test_read_file_lines_correct() -> None:
    """Test reading the lines of a file."""
    lines = ["unos", "dos", ""]
    temp_file = tempfile.NamedTemporaryFile("w")
    temp_file.write("".join([line + "\n" for line in lines]))
    temp_file.flush()

    temp_path = Path(temp_file.name)
    read_lines = list(read_file_lines(temp_path))

    assert len(read_lines) == len(lines) - 1, "The number of lines is invalid."
    for line, read_line in zip(lines, read_lines):
        assert line == read_line, f'Lines differs: "{line}" != "{read_line}".'


def test_read_file_lines_from_inexistent_file() -> None:
    """Test if an exception is raised when an inexistent file is given."""
    path = Path("/root/another_file_that_i_am_quite_sure_it_not_exists.txt")

    with pytest.raises(
        (ImproperPermissionsException, FileNotExists)
    ) as execution:
        read_file_lines(path)

    exception_raised = execution.value
    assert exception_raised, "The inexistent file was actually manipulated."
