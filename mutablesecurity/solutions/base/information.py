"""Module defining an abstract information."""

import typing
from abc import abstractmethod
from enum import Enum

from pyinfra import host
from pyinfra.api import FactBase

from mutablesecurity.helpers.exceptions import (
    EnumTypeNotSetException,
    InvalidInformationValueException,
    InvalidInformationValueToConvert,
    MandatoryAspectLeftUnsetException,
    NonWritableInformationException,
    SolutionInformationNotFoundException,
    SolutionObjectNotFoundException,
)
from mutablesecurity.solutions.base.object import BaseManager, BaseObject
from mutablesecurity.solutions.base.result import (
    BaseConcreteResultObjects,
    BaseGenericObjectsDescriptions,
    KeysDescriptions,
)

Operation = typing.Annotated[typing.Callable, "pyinfra Operation"]


class InnerInformationType(Enum):
    """Enumeration for possible types for an information."""

    __BASIC_TYPES_BASE = 0
    INTEGER = __BASIC_TYPES_BASE + 1
    STRING = __BASIC_TYPES_BASE + 2
    ENUM = __BASIC_TYPES_BASE + 3

    __LIST_BASE = 10
    LIST_OF_INTEGERS = __LIST_BASE + 0
    LIST_OF_STRINGS = __LIST_BASE + 1
    LIST_OF_ENUMS = __LIST_BASE + 2


class InformationType:
    """Class for wrapping the information types."""

    INNER_TYPE: InnerInformationType
    BASE_ENUM: typing.Type[Enum]

    def __new__(  # pylint: disable=unused-argument
        cls: typing.Type["InformationType"], *args: tuple, **kwargs: typing.Any
    ) -> "InformationType":
        """Initialize the class after definition.

        Args:
            args (tuple): Positional arguments
            kwargs (typing.Any): Keyword arguments

        Raises:
            EnumTypeNotSetException: The child type of exception is not
                specified.

        Returns:
            InformationType: Class
        """
        if (
            cls.INNER_TYPE
            in [
                InnerInformationType.ENUM,
                InnerInformationType.LIST_OF_ENUMS,
            ]
            and cls.BASE_ENUM is None
        ):
            raise EnumTypeNotSetException()

        instance: "InformationType" = super(InformationType, cls).__new__(cls)

        return instance

    @classmethod
    def name(cls: typing.Type["InformationType"]) -> str:
        """Get the name of the underlying type.

        Returns:
            str: Name
        """
        return cls.INNER_TYPE.name

    @classmethod
    def convert_string(
        cls: typing.Type["InformationType"],
        string: str,
    ) -> typing.Union[
        int, str, Enum, typing.List[int], typing.List[str], typing.List[Enum]
    ]:
        """Convert a string into its original representation.

        Args:
            string (str): Stringified information value

        Raises:
            InvalidInformationValueToConvert: The provided value is invalid.

        Returns:
            typing.Union[ int, str, Enum, typing.List[int], typing.List[str], \
                typing.List[Enum] ]: Converted value
        """
        try:
            if cls.INNER_TYPE == InnerInformationType.INTEGER:
                return int(string)
            elif cls.INNER_TYPE == InnerInformationType.ENUM:
                return cls.BASE_ENUM(string)
            elif cls.INNER_TYPE == InnerInformationType.LIST_OF_INTEGERS:
                int_list = string.split(",")

                return [int(elem) for elem in int_list]
            elif cls.INNER_TYPE == InnerInformationType.LIST_OF_STRINGS:
                return string.split(",")
            elif cls.INNER_TYPE == InnerInformationType.LIST_OF_ENUMS:
                enum_list = string.split(",")

                return [cls.BASE_ENUM(elem) for elem in enum_list]

            return string

        except (KeyError, ValueError) as exception:
            raise InvalidInformationValueToConvert() from exception

    def __str__(self) -> str:
        """Stringify the object.

        Returns:
            str: String representation
        """
        return self.INNER_TYPE.name

    def __repr__(self) -> str:
        """Represent the object.

        Returns:
            str: String representation
        """
        return self.INNER_TYPE.name


class IntegerInformationType(InformationType):
    """Information type for integer."""

    ALIAS = "INTEGER"
    INNER_TYPE = InnerInformationType.INTEGER


class StringInformationType(InformationType):
    """Information type for strings."""

    ALIAS = "STRING"
    INNER_TYPE = InnerInformationType.STRING


class IntegerListInformationType(InformationType):
    """Information type for list of integers."""

    ALIAS = "LIST OF INTEGERS"
    INNER_TYPE = InnerInformationType.LIST_OF_INTEGERS


class StringListInformationType(InformationType):
    """Information type for list of strings."""

    ALIAS = "LIST OF STRINGS"
    INNER_TYPE = InnerInformationType.LIST_OF_STRINGS


class InformationProperties(Enum):
    """Enumeration for possible properties of an information."""

    # Base for information's type
    __TYPE_BASE = 0

    # Writable information on which depends the functioning of the solution
    CONFIGURATION = __TYPE_BASE + 1

    # Read-only information that is exposed by the solution, describing its
    # functioning
    METRIC = __TYPE_BASE + 2

    # Base for configuration's optionality
    __CONFIGURATION_OPTIONALITY_BASE = 10

    # Required to be set during the whole functioning of the solution
    MANDATORY = __CONFIGURATION_OPTIONALITY_BASE + 1

    # Optional to set
    OPTIONAL = __CONFIGURATION_OPTIONALITY_BASE + 2

    # Base for configuration's generation mechanism
    _CONFIGURATION_VALUE_GENERATION_BASE = 100

    # With a value auto-generated on installation
    AUTO_GENERATED = _CONFIGURATION_VALUE_GENERATION_BASE + 1

    # With a default (recommended) value
    WITH_DEFAULT_VALUE = _CONFIGURATION_VALUE_GENERATION_BASE + 2

    def __str__(self) -> str:
        """Stringify the object.

        Returns:
            str: String representation
        """
        return self.name

    def __repr__(self) -> str:
        """Represent the object.

        Returns:
            str: String representation
        """
        return self.name


class BaseInformation(BaseObject):
    """Abstract class modeling an information related to the solution.

    As the information is the only part of a solution that is stateful (can be
    useful for the effective operations), the actual value is stored inside the
    host data.
    """

    DEFAULT_VALUE: typing.Any
    INFO_TYPE: typing.Type[InformationType]
    PROPERTIES: typing.List[InformationProperties]
    GETTER: FactBase
    SETTER: Operation

    @staticmethod
    def __ensure_exists_on_host() -> None:
        """Ensure that the information can be stored in the host data."""
        if "mutablesecurity" not in host.host_data:
            host.host_data["mutablesecurity"] = {}

    @classmethod
    def get_actual_value(cls: typing.Type["BaseInformation"]) -> typing.Any:
        """Get the actual value of the property, as stored in the host data.

        Returns:
            typing.Any: Value
        """
        cls.__ensure_exists_on_host()

        try:
            return host.host_data["mutablesecurity"][cls.IDENTIFIER]
        except KeyError:
            return None

    @classmethod
    def set_actual_value(
        cls: typing.Type["BaseInformation"], value: typing.Any
    ) -> None:
        """Set a value as the actual one, in the host data.

        Args:
            value (typing.Any): Value to set
        """
        cls.__ensure_exists_on_host()

        host.host_data["mutablesecurity"][cls.IDENTIFIER] = value

    @staticmethod
    @abstractmethod
    def validate_value(value: typing.Any) -> bool:
        """Validate if the information's value is valid.

        Args:
            value (typing.Any): Value of the information

        Returns:
            bool: Boolean indicating if the information is valid
        """


class InformationManager(BaseManager):
    """Class managing the information of a solution."""

    objects_descriptions: BaseGenericObjectsDescriptions
    KEYS_DESCRIPTIONS: KeysDescriptions = {
        "identifier": "Identifier",
        "description": "Description",
        "type": "Type",
        "properties": "Properties",
        "default_value": "Default Value",
    }

    def __init__(self, information: typing.Sequence[BaseInformation]) -> None:
        """Initialize the instance.

        Args:
            information (typing.Sequence[BaseInformation]): List of information
                to be added
        """
        super().__init__(information)

        self.objects_descriptions = [
            {
                "identifier": info.IDENTIFIER,
                "description": info.DESCRIPTION,
                "type": info.INFO_TYPE,
                "properties": info.PROPERTIES,
                "default_value": info.DEFAULT_VALUE,
            }
            for info in information
        ]

    def get(
        self, identifier: typing.Optional[str]
    ) -> BaseConcreteResultObjects:
        """Get a specific information or all of them.

        Args:
            identifier (str, optional): Information identifier. Defaults to
                None in case all the information will be retrieved.

        Raises:
            SolutionInformationNotFoundException: The identifier does not
                correspond to any information.

        Returns:
            BaseConcreteResultObjects: Result containing the requested
                information
        """
        # Get the information list
        if identifier:
            try:
                info: BaseInformation = self.get_object_by_identifier(
                    identifier
                )  # type: ignore[assignment]
            except SolutionObjectNotFoundException as exception:
                raise SolutionInformationNotFoundException() from exception

            info_list = [info]

        else:
            info_list = list(self.objects.values())  # type: ignore[arg-type]

        # Get the concrete values
        for info in info_list:
            info.set_actual_value(host.get_fact(info.GETTER))

        return self.represent_as_dict(identifier=identifier)

    def set(
        self,
        identifier: str,
        value: typing.Any,
        only_local: typing.Optional[bool] = False,
    ) -> None:
        """Set an information value.

        Args:
            identifier (str): Information identifier
            value (typing.Any): New value
            only_local (typing.Optional[bool]): Boolean indicating if the
                changes are local-only. Defaults to False, indicating the fact
                that the remote host is involved in the process.

        Raises:
            SolutionInformationNotFoundException: The information identified
                by the provided key was not found.
            InvalidInformationValueException: The new value is incorrect.
            NonWritableInformationException: The information is not writable.
        """
        try:
            info: BaseInformation = self.get_object_by_identifier(
                identifier
            )  # type: ignore[assignment]
        except SolutionObjectNotFoundException as exception:
            raise SolutionInformationNotFoundException() from exception

        if InformationProperties.CONFIGURATION not in info.PROPERTIES:
            raise NonWritableInformationException()

        actual_value = info.INFO_TYPE.convert_string(value)
        if not info.validate_value(actual_value):
            raise InvalidInformationValueException()

        if not only_local:
            info.SETTER(actual_value)

        info.set_actual_value(actual_value)

    def set_default_values_locally(self) -> None:
        """Set the default values in the local configuration."""
        for _, raw_info in self.objects.items():
            info: BaseInformation = raw_info  # type: ignore[assignment]

            if InformationProperties.WITH_DEFAULT_VALUE in info.PROPERTIES:
                info.set_actual_value(info.DEFAULT_VALUE)

    def set_all_from_dict_locally(self, export: dict) -> None:
        """Set all the local values from an export dictionary.

        Args:
            export (dict): Previously exported dictionary
        """
        for key, value in export.items():
            self.set(key, value, only_local=True)

        self.validate_all()

    def validate_all(
        self, filter_property: typing.Optional[InformationProperties] = None
    ) -> None:
        """Validate if the stored information is set accordingly as a whole.

        The value is not validated as an exception is already raised on setting
        methods.

        Args:
            filter_property (InformationProperties, optional): Filter for
                information stored in the manager

        Raises:
            MandatoryAspectLeftUnsetException: One mandatory aspect is left
                unset.
        """
        for _, raw_info in self.objects.items():
            info: BaseInformation = raw_info  # type: ignore[assignment]

            if filter_property and filter_property not in info.PROPERTIES:
                continue

            if (
                InformationProperties.MANDATORY in info.PROPERTIES
                and not info.get_actual_value()
            ):
                raise MandatoryAspectLeftUnsetException()

    def represent_as_dict(
        self,
        identifier: str = None,
        filter_property: typing.Optional[InformationProperties] = None,
    ) -> BaseConcreteResultObjects:
        """Get the (filtered) information as a dictionary.

        Args:
            filter_property (InformationProperties, optional): Mandatory
                properties for the information returned. Defaults to None.
            identifier (str): Identifier of the single information to represent
                in the string. Defaults to None.

        Returns:
            BaseConcreteResultObjects: Resulted dictionary
        """
        result = {}
        for key, current_info in self.objects.items():
            info: BaseInformation = current_info  # type: ignore[assignment]

            if identifier and info.IDENTIFIER != identifier:
                continue

            if filter_property and filter_property not in info.PROPERTIES:
                continue

            result[key] = info.get_actual_value()

        return result
