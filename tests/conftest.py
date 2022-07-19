"""pytest configuration."""
import os
import typing

import pytest

from mutablesecurity.config import ConfigurationManager


@pytest.fixture(autouse=True)
def preserve_test_config_file() -> typing.Generator[None, None, None]:
    """Automatically save + restore or delete the configuration file.

    Yields:
        typing.Generator[None, None, None]: None
    """
    content = None
    if os.path.exists(ConfigurationManager.CONFIGURATION_FILENAME):
        content = open(
            ConfigurationManager.CONFIGURATION_FILENAME, "r", encoding="utf-8"
        ).read()

    yield

    if content:
        with open(
            ConfigurationManager.CONFIGURATION_FILENAME, "w", encoding="utf-8"
        ) as config_file:
            config_file.write(content)
    else:
        os.remove(ConfigurationManager.CONFIGURATION_FILENAME)
