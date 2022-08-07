"""Module for working with a local, user-defined configuration."""

import typing

from mutablesecurity.config.config import ConfigurationManager
from mutablesecurity.helpers.exceptions import (
    InvalidStructureOfLocalConfigException,
    InvalidValueInLocalConfigException,
)


def __getattr__(name: str) -> typing.Any:
    """Redirect a member access in this module to the manager.

    Args:
        name (str): Member name to access

    Returns:
        typing.Any: Member value
    """
    if name == "ConfigurationManager":
        return ConfigurationManager

    return getattr(ConfigurationManager(), name)


def set_manually(name: str, value: typing.Any) -> None:
    """Redirect the member setting in this module to the manager.

    Args:
        name (str): Member name to set
        value (typing.Any): New member value
    """
    setattr(ConfigurationManager(), name, value)


def reload() -> None:
    """Reload the configuration stored in the manager.

    Raises:
        InvalidStructureOfLocalConfigException: See the constructor.
        InvalidValueInLocalConfigException: See the constructor.
    """
    try:
        ConfigurationManager.__init__(ConfigurationManager())
    except (
        InvalidStructureOfLocalConfigException,
        InvalidValueInLocalConfigException,
    ) as exception:
        raise exception
