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


class IntegerInformationType(InformationType):
    """Information type for integer."""

    INNER_TYPE = InnerInformationType.INTEGER


class StringInformationType(InformationType):
    """Information type for strings."""

    INNER_TYPE = InnerInformationType.STRING


class IntegerListInformationType(InformationType):
    """Information type for list of integers."""

    INNER_TYPE = InnerInformationType.LIST_OF_INTEGERS


class StringListInformationType(InformationType):
    """Information type for list of strings."""

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


class BaseInformation(BaseObject):
    """Abstract class modeling an information related to the solution."""

    DEFAULT_VALUE: typing.Any
    INFO_TYPE: typing.Type[InformationType]
    PROPERTIES: typing.List[InformationProperties]
    GETTER: FactBase
    SETTER: Operation
    actual_value: typing.Any = None

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

    def __init__(self, information: typing.Sequence[BaseInformation]) -> None:
        """Initialize the instance.

        Args:
            information (typing.Sequence[BaseInformation]): List of information
                to be added
        """
        super().__init__(information)

    def get(self, identifier: typing.Optional[str]) -> typing.Any:
        """Get a specific information or all of them.

        Args:
            identifier (str, optional): Information identifier. Defaults to
                None in case all the information will be retrieved.

        Raises:
            SolutionInformationNotFoundException: The identifier does not
                correspond to any information.

        Returns:
            typing.Any: Information value or dictionary with keys - information
                value
        """
        if identifier:
            try:
                info: BaseInformation = self.get_object_by_identifier(
                    identifier
                )  # type: ignore
            except SolutionObjectNotFoundException as exception:
                raise SolutionInformationNotFoundException() from exception

            info_list = [info]

        else:
            info_list = list(self.objects.values())  # type: ignore

        for info in info_list:
            if InformationProperties.CONFIGURATION not in info.PROPERTIES:
                info.actual_value = host.get_fact(info.GETTER)  # type: ignore

        if identifier:
            return info_list[0].actual_value

        return self.get_all_as_dict()

    def get_all_as_dict(
        self, filter_property: typing.Optional[InformationProperties] = None
    ) -> dict:
        """Get the (filtered) information as a dictionary.

        Args:
            filter_property (InformationProperties, optional): Mandatory
                properties for the information returned. Defaults to None.

        Returns:
            dict: Resulted dictionary
        """
        result = {}
        for key, current_info in self.objects.items():
            info: BaseInformation = current_info  # type: ignore
            if filter_property and filter_property not in info.PROPERTIES:
                continue

            result[key] = info.actual_value

        return result

    def set(self, identifier: str, value: typing.Any) -> None:
        """Set an information value.

        Args:
            identifier (str): Information identifier
            value (typing.Any): New value

        Raises:
            SolutionInformationNotFoundException: The information identified
                by the provided key was not found.
            InvalidInformationValueException: The new value is incorrect.
            NonWritableInformationException: The information is not writable.
        """
        try:
            info: BaseInformation = self.get_object_by_identifier(
                identifier
            )  # type: ignore
        except SolutionObjectNotFoundException as exception:
            raise SolutionInformationNotFoundException() from exception

        actual_value = info.INFO_TYPE.convert_string(value)

        if InformationProperties.CONFIGURATION not in info.PROPERTIES:
            raise NonWritableInformationException()

        if not info.validate_value(actual_value):
            raise InvalidInformationValueException()

        info.SETTER(actual_value)
        info.actual_value = actual_value

    def set_default_values(self) -> None:
        """Set the default values to configuration."""
        for _, raw_info in self.objects.items():
            info: BaseInformation = raw_info  # type: ignore

            if InformationProperties.CONFIGURATION in info.PROPERTIES:
                info.actual_value = info.DEFAULT_VALUE  # type: ignore

    def set_all_from_dict(self, export: dict) -> None:
        """Set all the values from an export dictionary.

        Args:
            export (dict): Previously exported dictionary
        """
        for key, value in export.items():
            self.set(key, value)

    def validate(
        self, filter_property: typing.Optional[InformationProperties] = None
    ) -> None:
        """Check if all the information is set accordingly.

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
            info: BaseInformation = raw_info  # type: ignore

            if filter_property and filter_property not in info.PROPERTIES:
                continue

            if (
                InformationProperties.MANDATORY in info.PROPERTIES
                and not info.actual_value
            ):
                raise MandatoryAspectLeftUnsetException()

    def represent_as_matrix(
        self,
        generic: bool = False,
    ) -> typing.List[typing.List[str]]:
        """Represent the information as a matrix.

        Args:
            generic (bool): Boolean indicating if the matrix representation is
                generic, without any concrete value (for example, the actual
                value) included. Defaults to False.

        Returns:
            typing.List[typing.List[str]]: Matrix with details about the
                solution's information.
        """
        header = [
            "Identifier",
            "Description",
            "Type",
            "Properties",
            "Default Value",
        ]
        if not generic:
            header.append("Actual Value")

        result = [header]
        for key, raw_info in self.objects.items():
            info: BaseInformation = raw_info  # type: ignore
            properties = ", ".join([prop.name for prop in info.PROPERTIES])
            default_value = (
                str(info.DEFAULT_VALUE) if info.DEFAULT_VALUE else "-"
            )

            row = [
                key,
                info.DESCRIPTION,
                info.INFO_TYPE.name(),
                properties,
                default_value,
            ]

            if not generic:
                row.append(str(info.actual_value))
            result.append(row)

        return result
