"""Module for dealing with plain (single level) YAML files."""
import os
import typing
from enum import Enum

import yaml

from mutablesecurity.helpers.exceptions import (
    NotPlainDictionaryException,
    YAMLFileNotExistsException,
    YAMLKeyMissingException,
)


def __is_plain_dict(dictionary: dict) -> bool:
    for key, value in dictionary.items():
        # Check the keys to be strings
        if not isinstance(key, str):
            return False

        # Check the values to be integers, strings, enumerations or lists of
        # the previously mentioned types.
        if not (
            isinstance(value, int)
            or isinstance(value, str)
            or isinstance(value, Enum)
            or value is None
            or (
                isinstance(value, list)
                and (
                    all(isinstance(elem, int) for elem in value)
                    or all(isinstance(elem, str) for elem in value)
                    or all(isinstance(elem, Enum) for elem in value)
                )
            )
        ):
            return False

    return True


def load_from_file(
    filename: str, mandatory_keys: typing.Optional[typing.List[str]] = None
) -> dict:
    """Load a plain dictionary from a YAML file.

    Args:
        filename (str): YAML filename
        mandatory_keys (typing.List[str]): List of mandatory keys present in
            the loaded content. Defaults to None.

    Raises:
        YAMLFileNotExistsException: The file does not exists.
        NotPlainDictionaryException: The read dictionary is not plain.
        YAMLKeyMissingException: Mandatory key not present

    Returns:
        dict: Plain dictionary
    """
    if not os.path.isfile(filename):
        raise YAMLFileNotExistsException()

    with open(filename, mode="r", encoding="utf-8") as yaml_file:
        raw_content = yaml_file.read()
        content = yaml.safe_load(raw_content)
        if not __is_plain_dict(content):
            raise NotPlainDictionaryException()

        if mandatory_keys:
            for key in mandatory_keys:
                if key not in content:
                    raise YAMLKeyMissingException()

        return content


def dump_to_file(content: dict, filename: str) -> None:
    """Dump a plain dictionary to a YAML file.

    Args:
        content (dict): Plain dictionary
        filename (str): YAML filename

    Raises:
        NotPlainDictionaryException: The dictionary is not plain.
    """
    if not __is_plain_dict(content):
        raise NotPlainDictionaryException()

    raw_content = yaml.dump(content, Dumper=yaml.SafeDumper)

    # skipcq: PTC-W6004
    with open(filename, mode="w", encoding="utf-8") as yaml_file:
        yaml_file.write(raw_content)
