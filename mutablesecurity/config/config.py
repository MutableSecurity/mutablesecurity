"""Module implementing the configuration manager of MutableSecurity."""
import typing
from enum import Enum

from pypattyrn.creational.singleton import Singleton

from mutablesecurity.helpers.data_type import BooleanDataType, DataType
from mutablesecurity.helpers.exceptions import (
    InvalidDataValueToConvertException,
    InvalidStructureOfLocalConfigException,
    InvalidValueInLocalConfigException,
    InvalidValueToSetInLocalConfigException,
    NoKeyInLocalConfigException,
    NotPlainDictionaryException,
    YAMLFileNotExistsException,
)
from mutablesecurity.helpers.plain_yaml import load_from_file


class ConfigurationKey:
    """Class for storing data about each key in the configuration."""

    key: str
    data_type: typing.Type[DataType]
    default_value: typing.Any

    def __init__(
        self,
        key: str,
        data_type: typing.Type[DataType],
        default_value: typing.Any = None,
    ) -> None:
        """Initialize the instance.

        Args:
            key (str): Key in the YAML configuration file
            data_type (typing.Type[DataType]): Value type
            default_value (typing.Any): Default value when the key is not
                specified. Defaults to None.
        """
        self.key = key
        self.data_type = data_type
        if default_value is not None:
            self.default_value = default_value


class ConfigurationManager(metaclass=Singleton):
    """Class for managing the user-specific, optional configuration."""

    CONFIGURATION_FILENAME = ".mutablesecurity"
    configuration: typing.Dict[str, typing.Any]

    class ConfigurationKeys(Enum):
        """Enumeration for all the keys from the configuration file."""

        DEVELOPER_MODE = ConfigurationKey(
            "developer_mode",
            BooleanDataType,
            default_value=False,
        )

    def __init__(self) -> None:
        """Initialize the configuration manager instance.

        Raises:
            InvalidStructureOfLocalConfigException: The local configuration
                file has an invalid structure.
            InvalidValueInLocalConfigException: An invalid value was specified
                in the configuration file.
        """
        try:
            loaded_config = load_from_file(
                ConfigurationManager.CONFIGURATION_FILENAME
            )
        except NotPlainDictionaryException as exception:
            raise InvalidStructureOfLocalConfigException() from exception
        except YAMLFileNotExistsException:
            loaded_config = {}

        self.configuration = {}
        for key in ConfigurationManager.ConfigurationKeys:
            config_key: ConfigurationKey = key.value
            effective_key = config_key.key
            key_type = config_key.data_type

            if effective_key not in loaded_config:
                value = config_key.default_value
            else:
                value = loaded_config[effective_key]

            # If a value is specified, try to convert it to its real type
            if key_type.validate_data(value):
                self.configuration[effective_key] = value
            else:
                try:
                    self.configuration[
                        effective_key
                    ] = key_type.convert_string(value)
                except InvalidDataValueToConvertException as exception:
                    raise InvalidValueInLocalConfigException() from exception

    def __getattribute__(self, name: str) -> typing.Any:
        """Redirect the member access to the internal configuration dictionary.

        Args:
            name (str): Argument name

        Returns:
            typing.Any: Argument value
        """
        config_dict = super().__getattribute__("configuration")

        if name == "configuration":
            return config_dict
        elif name == "__init__":
            return ConfigurationManager.__init__

        try:
            return config_dict[name]
        except KeyError:
            return None

    def __setattr__(self, name: str, value: str) -> None:
        """Redirect the attribute setting to the inner dictionary.

        Args:
            name (str): Attribute name
            value (str): Attribute value

        Raises:
            NoKeyInLocalConfigException: The key is not present in the
                local configuration.
            InvalidValueToSetInLocalConfigException: The set value is invalid.
        """
        if name == "configuration":
            super().__setattr__("configuration", value)

            return

        config_dict = super().__getattribute__("configuration")

        present = False
        for key in ConfigurationManager.ConfigurationKeys:
            config_key: ConfigurationKey = key.value

            if config_key.key == name:
                present = True
                break

        if name not in config_dict and not present:
            raise NoKeyInLocalConfigException()

        if not config_key.data_type.validate_data(value):
            raise InvalidValueToSetInLocalConfigException()

        config_dict[name] = value
        super().__setattr__("configuration", config_dict)
