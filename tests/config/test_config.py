"""Module for testing the MutableSecurity configuration."""


import pytest

from mutablesecurity import config
from mutablesecurity.config import ConfigurationManager
from mutablesecurity.helpers.exceptions import (
    InvalidStructureOfLocalConfigException,
    InvalidValueInLocalConfigException,
    InvalidValueToSetInLocalConfigException,
    NoKeyInLocalConfigException,
)

DEV_KEY = ConfigurationManager.ConfigurationKeys.DEVELOPER_MODE.value.key


class InvalidType:
    """Dummy class for an invalid type."""


def __place_text_config(text_config: str) -> None:
    with open(
        ConfigurationManager.CONFIGURATION_FILENAME, "w", encoding="utf-8"
    ) as config_file:
        config_file.write(text_config)


def test_valid_configuration() -> None:
    """Test the dumping, loading and setting of a plain dictionary."""
    text_config = f"{DEV_KEY}: True"
    __place_text_config(text_config)

    config.reload()

    assert getattr(
        config, DEV_KEY
    ), f"The key {DEV_KEY} was not saved and returned correctly."

    setattr(config, DEV_KEY, False)

    assert not getattr(config, DEV_KEY), (
        f"The key {DEV_KEY} was not saved and returned correctly after manual"
        " setting."
    )


def test_invalid_structure_configuration() -> None:
    """Test the testing an unstructured configuration file."""
    text_config = f"{DEV_KEY}:\n  fail: True"
    __place_text_config(text_config)

    with pytest.raises(InvalidStructureOfLocalConfigException) as execution:
        config.reload()

    exception_raised = execution.value
    assert (
        exception_raised
    ), "An error was not raised when accessing an unstructured configuration."


def test_invalid_value_configuration() -> None:
    """Test the testing a configuration file with an invalid value."""
    text_config = f"{DEV_KEY}: fail"
    __place_text_config(text_config)

    with pytest.raises(InvalidValueInLocalConfigException) as execution:
        config.reload()
    assert execution.value, (
        "An error was not raised when accessing a configuration with an"
        " invalid value."
    )


def test_invalid_member_setting() -> None:
    """Test invalid setting of configuration keys."""
    text_config = f"{DEV_KEY}: True"
    __place_text_config(text_config)

    config.reload()

    with pytest.raises(NoKeyInLocalConfigException) as key_execution:
        config.set_manually("too_unusual_to_exist", InvalidType())
    assert (
        key_execution.value
    ), "An error was not raised when setting a key that does not exists."

    with pytest.raises(
        InvalidValueToSetInLocalConfigException
    ) as value_execution:
        config.set_manually(DEV_KEY, InvalidType())
    assert value_execution.value, (
        "An error was not raised when accessing a configuration with an"
        " invalid value."
    )
