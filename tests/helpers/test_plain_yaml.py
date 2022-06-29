"""Module for testing the plain YAML parsing."""

import tempfile

import pytest

from src.helpers.exceptions import (
    NotPlainDictionaryException,
    YAMLFileNotExistsException,
    YAMLKeyMissingException,
)
from src.helpers.plain_yaml import dump_to_file, load_from_file


def test_valid_load_dump() -> None:
    """Test the dumping and loading of a plain dictionary."""
    test_dict = {"id": 1, "name": "test", "array": [1, 2, 3]}
    temp_file = tempfile.NamedTemporaryFile("w")

    dump_to_file(test_dict, temp_file.name)
    loaded_test_dict = load_from_file(temp_file.name)

    for key, value in test_dict.items():
        assert (
            key in loaded_test_dict
        ), f"The key {key} is not present in the loaded dictionary."

        assert value == loaded_test_dict[key], (
            f"The value from key {key} does not have the correct value in the"
            f" loaded dictionary: {value} != {loaded_test_dict[key]}."
        )


def test_invalid_multilevel_dict() -> None:
    """Test if an exception is raised when passing a multi-level dictionary."""
    test_dict = {"outside": {"inside": "heh"}}

    temp_file = tempfile.NamedTemporaryFile("w")

    with pytest.raises(NotPlainDictionaryException) as execution:
        dump_to_file(test_dict, temp_file.name)

    exception_raised = execution.value
    assert exception_raised, "The multi-level dictionary was not detected."


def test_no_input_file() -> None:
    """Test if an exception is raised when opening an inexistent file."""
    with pytest.raises(YAMLFileNotExistsException) as execution:
        load_from_file("/root/pretty_sure_this_not_exists.yaml")

    exception_raised = execution.value
    assert exception_raised, "The non-existent YAML file was not detected."


def test_missing_required_key() -> None:
    """Test if an exception is raised when a mandatory key is not present."""
    test_dict = {"key": "value"}
    temp_file = tempfile.NamedTemporaryFile("w")

    dump_to_file(test_dict, temp_file.name)

    with pytest.raises(YAMLKeyMissingException) as execution:
        load_from_file(temp_file.name, ["key", "error"])

    exception_raised = execution.value
    assert exception_raised, "The missing required key was not detected."
